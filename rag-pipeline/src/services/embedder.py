"""Cohere embedding generation service."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp

import structlog

from ..config import PipelineConfig
from ..models.chunk import TextChunk
from ..models.embedding import Embedding
from ..utils.retry import retry_with_exponential_backoff

logger = structlog.get_logger(__name__)


class CohereEmbedder:
    """Generates embeddings using Cohere API."""

    COHERE_API_URL = "https://api.cohere.com/v2/embed"

    def __init__(self, config: PipelineConfig):
        """Initialize embedder with configuration.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.batch_size = config.cohere_batch_size
        self.max_rpm = config.cohere_max_rpm
        self.request_delay = 60.0 / self.max_rpm if self.max_rpm > 0 else 0.6

    async def close(self):
        """Close the embedder."""
        pass

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts using Cohere API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        async def _embed():
            payload = {
                "model": self.config.cohere_model,
                "texts": texts,
                "input_type": "search_document",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.COHERE_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.config.cohere_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Cohere API error: {response.status} - {error_text}")

                    result = await response.json()

                    # Handle different response formats
                    raw_embeddings = result.get("embeddings", {})

                    if isinstance(raw_embeddings, dict):
                        # API may return {"float": [[...], [...], ...]} or {"0": [...], "1": [...]}
                        if "float" in raw_embeddings:
                            embeddings = raw_embeddings["float"]
                        else:
                            embeddings = [raw_embeddings[str(i)] for i in range(len(texts))]
                    elif isinstance(raw_embeddings, list):
                        # API returned list of lists [[...], [...], ...]
                        embeddings = raw_embeddings
                    else:
                        raise Exception(f"Unexpected embeddings format: {type(raw_embeddings)}")

                    return embeddings

        # Retry with exponential backoff
        embeddings = await retry_with_exponential_backoff(
            _embed,
            max_retries=5,
            base_delay=2.0,
            max_delay=60.0,
            exceptions=(aiohttp.ClientError, asyncio.TimeoutError, Exception),
        )

        return embeddings

    async def embed_chunks(
        self, chunks: list[TextChunk], progress_callback=None
    ) -> list[Embedding]:
        """Embed multiple text chunks.

        Args:
            chunks: List of TextChunks to embed
            progress_callback: Optional callback for progress updates

        Returns:
            List of Embedding objects
        """
        embeddings = []
        total = len(chunks)
        processed = 0

        # Process in batches
        for i in range(0, total, self.batch_size):
            batch = chunks[i : i + self.batch_size]
            batch_texts = [chunk.text for chunk in batch]

            # Rate limiting
            await asyncio.sleep(self.request_delay)

            try:
                batch_embeddings = await self.embed_texts(batch_texts)

                for chunk, vector in zip(batch, batch_embeddings):
                    embedding = Embedding(
                        chunk_id=chunk.chunk_id,
                        vector=vector,
                        model=self.config.cohere_model,
                        chunk_ref=chunk,
                    )
                    embeddings.append(embedding)

                processed += len(batch)

                if progress_callback:
                    progress_callback(processed, total)

                logger.debug(
                    "batch_embedded",
                    batch_start=i,
                    batch_size=len(batch),
                    total=total,
                )

            except Exception as e:
                logger.error(
                    "batch_embed_failed",
                    batch_start=i,
                    batch_size=len(batch),
                    error=str(e),
                )
                raise

        logger.info(
            "all_chunks_embedded",
            total_chunks=total,
            total_embeddings=len(embeddings),
        )

        return embeddings

    async def embed_single(self, text: str) -> list[float]:
        """Embed a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = await self.embed_texts([text])
        return embeddings[0] if embeddings else []


def save_embeddings_to_jsonl(
    embeddings: list[Embedding], output_path: str
) -> int:
    """Save embeddings to JSONL format.

    Args:
        embeddings: List of Embedding objects
        output_path: Path to output file

    Returns:
        Number of embeddings saved
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w") as f:
        for embedding in embeddings:
            record = {
                "chunk_id": embedding.chunk_id,
                "vector": embedding.vector,
                "model": embedding.model,
                "created_at": embedding.created_at.isoformat(),
                "metadata": {
                    "text": embedding.chunk_ref.text if embedding.chunk_ref else "",
                    "url": embedding.chunk_ref.source_url if embedding.chunk_ref else "",
                    "title": embedding.chunk_ref.source_title if embedding.chunk_ref else "",
                    "chunk_index": embedding.chunk_ref.chunk_index if embedding.chunk_ref else 0,
                    "total_chunks": embedding.chunk_ref.total_chunks if embedding.chunk_ref else 0,
                    "token_count": embedding.chunk_ref.token_count if embedding.chunk_ref else 0,
                    **(embedding.chunk_ref.metadata if embedding.chunk_ref else {}),
                },
            }
            f.write(json.dumps(record) + "\n")

    logger.info("embeddings_saved", path=str(output_path), count=len(embeddings))
    return len(embeddings)


def load_embeddings_from_jsonl(
    input_path: str, limit: Optional[int] = None
) -> list[Embedding]:
    """Load embeddings from JSONL format.

    Args:
        input_path: Path to input file
        limit: Optional limit on number to load

    Returns:
        List of Embedding objects
    """
    input_file = Path(input_path)
    if not input_file.exists():
        return []

    embeddings = []
    with input_file.open("r") as f:
        for line in f:
            if limit and len(embeddings) >= limit:
                break

            record = json.loads(line.strip())
            embedding = Embedding(
                chunk_id=record["chunk_id"],
                vector=record["vector"],
                model=record.get("model", "embed-english-v3.0"),
                created_at=datetime.fromisoformat(record.get("created_at", datetime.utcnow().isoformat())),
            )
            embeddings.append(embedding)

    logger.info("embeddings_loaded", path=str(input_path), count=len(embeddings))
    return embeddings
