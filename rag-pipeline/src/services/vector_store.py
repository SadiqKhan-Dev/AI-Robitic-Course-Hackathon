"""Qdrant vector storage service."""

import asyncio
import json
from datetime import datetime
from typing import Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType,
)
from qdrant_client.http.exceptions import ResponseHandlingException

import structlog

from ..config import PipelineConfig
from ..models.embedding import Embedding, VectorRecord
from ..services.state_manager import StateManager
from ..utils.retry import retry_with_exponential_backoff

logger = structlog.get_logger(__name__)


class QdrantVectorStore:
    """Manages vector storage in Qdrant."""

    def __init__(self, config: PipelineConfig):
        """Initialize vector store with configuration.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.client: Optional[AsyncQdrantClient] = None
        self.batch_size = 100

    async def _get_client(self) -> AsyncQdrantClient:
        """Get or create Qdrant client."""
        if self.client is None:
            self.client = AsyncQdrantClient(
                url=self.config.qdrant_url,
                api_key=self.config.qdrant_api_key,
            )
        return self.client

    async def close(self):
        """Close the Qdrant client."""
        if self.client:
            await self.client.close()
            self.client = None

    async def create_collection(self, recreate: bool = False) -> bool:
        """Create the collection if it doesn't exist.

        Args:
            recreate: Whether to recreate if it exists

        Returns:
            True if collection was created, False if it already existed
        """
        client = await self._get_client()
        collection_name = self.config.qdrant_collection

        try:
            # Check if collection exists
            collections = await client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if collection_name in collection_names:
                if recreate:
                    logger.info("deleting_existing_collection", collection=collection_name)
                    await client.delete_collection(collection_name)
                else:
                    logger.info("collection_exists", collection=collection_name)
                    return False

            # Create collection
            logger.info("creating_collection", collection=collection_name)
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.config.embedding_dimensions,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload index on URL for filtering
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="url",
                field_schema=PayloadSchemaType.KEYWORD,
            )

            logger.info("collection_created", collection=collection_name)
            return True

        except Exception as e:
            logger.error("collection_creation_failed", error=str(e))
            raise

    async def connect(self) -> bool:
        """Test connection to Qdrant.

        Returns:
            True if connection successful
        """
        try:
            client = await self._get_client()
            collections = await client.get_collections()
            logger.info("connected", collections=[c.name for c in collections.collections])
            return True
        except Exception as e:
            logger.error("connection_failed", error=str(e))
            return False

    async def upload_embeddings(
        self,
        embeddings: list[Embedding],
        progress_callback=None,
    ) -> tuple[list[str], dict[str, str]]:
        """Upload embeddings to Qdrant.

        Args:
            embeddings: List of Embeddings to upload
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (uploaded_ids, failed_ids_with_errors)
        """
        client = await self._get_client()
        collection_name = self.config.qdrant_collection

        # Convert to VectorRecords
        records = [e.to_vector_record() for e in embeddings]

        # Upload in batches
        uploaded_ids = []
        failed = {}

        total = len(records)
        for i in range(0, total, self.batch_size):
            batch = records[i : i + self.batch_size]

            try:
                # Retry upload with exponential backoff
                await self._upload_batch(client, collection_name, batch)

                uploaded_ids.extend([r.id for r in batch])

                if progress_callback:
                    progress_callback(len(uploaded_ids), total)

                logger.debug(
                    "batch_uploaded",
                    batch_start=i,
                    batch_size=len(batch),
                    total=total,
                )

            except Exception as e:
                logger.error(
                    "batch_upload_failed",
                    batch_start=i,
                    batch_size=len(batch),
                    error=str(e),
                )
                # Try individual uploads
                for record in batch:
                    try:
                        await self._upload_batch(client, collection_name, [record])
                        uploaded_ids.append(record.id)
                    except Exception as inner_e:
                        failed[record.id] = str(inner_e)

        logger.info(
            "upload_complete",
            total=total,
            uploaded=len(uploaded_ids),
            failed=len(failed),
        )

        return uploaded_ids, failed

    async def _upload_batch(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
        records: list[VectorRecord],
    ):
        """Upload a batch of records.

        Args:
            client: Qdrant client
            collection_name: Name of collection
            records: List of VectorRecords to upload
        """
        # Convert to Qdrant points with numeric IDs (Qdrant requires integer or UUID IDs)
        points = []
        for idx, r in enumerate(records):
            point = r.to_qdrant_point()
            # Use numeric ID based on batch position
            from qdrant_client.models import PointStruct
            points.append(PointStruct(
                id=idx,  # Numeric ID
                vector=point.vector,
                payload=point.payload,
            ))

        async def _upsert():
            await client.upsert(collection_name=collection_name, points=points)

        await retry_with_exponential_backoff(
            _upsert,
            max_retries=5,
            base_delay=1.0,
            max_delay=60.0,
            exceptions=(ResponseHandlingException, Exception),
        )

    async def count_vectors(self) -> int:
        """Count total vectors in collection.

        Returns:
            Number of vectors in collection
        """
        client = await self._get_client()
        collection_name = self.config.qdrant_collection

        try:
            count_result = await client.count(collection_name)
            return count_result.count
        except Exception as e:
            logger.error("count_failed", error=str(e))
            return 0

    async def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results with metadata
        """
        client = await self._get_client()
        collection_name = self.config.qdrant_collection

        results = await client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload,
            }
            for r in results
        ]

    async def test_search(self, test_queries: list[str], embedder) -> dict:
        """Run test searches to validate the collection.

        Args:
            test_queries: List of query strings to search
            embedder: CohereEmbedder instance for generating query embeddings

        Returns:
            Dictionary with test results
        """
        results = {}

        for query in test_queries:
            try:
                # Generate query embedding
                query_embedding = await embedder.embed_single(query)

                # Search
                search_results = await self.search(
                    query_vector=query_embedding,
                    limit=5,
                    score_threshold=0.5,
                )

                results[query] = {
                    "found": len(search_results) > 0,
                    "top_score": search_results[0]["score"] if search_results else 0,
                    "result_count": len(search_results),
                }

            except Exception as e:
                results[query] = {"error": str(e)}

        return results


def load_embeddings_for_upload(
    input_file: str = "./data/embeddings.jsonl",
) -> list[Embedding]:
    """Load embeddings from JSONL file.

    Args:
        input_file: Path to embeddings JSONL file

    Returns:
        List of Embedding objects
    """
    from ..models.embedding import Embedding
    from ..models.chunk import TextChunk

    embeddings = []
    with open(input_file, "r") as f:
        for line in f:
            record = json.loads(line.strip())

            # Create minimal chunk_ref
            meta = record.get("metadata", {})
            chunk_ref = TextChunk(
                chunk_id=record["chunk_id"],
                text=meta.get("text", ""),
                source_url=meta.get("url", ""),
                source_title=meta.get("title", ""),
                chunk_index=meta.get("chunk_index", 0),
                total_chunks=meta.get("total_chunks", 0),
                token_count=meta.get("token_count", 0),
                char_start=0,
                char_end=len(meta.get("text", "")),
                metadata={k: v for k, v in meta.items() if k not in [
                    "text", "url", "title", "chunk_index", "total_chunks", "token_count"
                ]},
            )

            embedding = Embedding(
                chunk_id=record["chunk_id"],
                vector=record["vector"],
                model=record.get("model", "embed-english-v3.0"),
                created_at=datetime.fromisoformat(record.get("created_at", datetime.utcnow().isoformat())),
                chunk_ref=chunk_ref,
            )
            embeddings.append(embedding)

    return embeddings
