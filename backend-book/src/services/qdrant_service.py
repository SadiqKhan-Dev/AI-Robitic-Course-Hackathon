import uuid
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
from config.settings import settings
import logging


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_HOST,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=True
        )
        self.collection_name = "book_content"
        self.logger = logging.getLogger(__name__)
        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize the collection if it doesn't exist"""
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except Exception as e:
            self.logger.warning(f"Collection {self.collection_name} not found, creating it: {str(e)}")
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere embed-multilingual-v3.0 has 1024 dimensions
                    distance=models.Distance.COSINE
                )
            )

    def store_embeddings(self, content_chunks: List[dict]):
        """
        Store content chunks with their embeddings in Qdrant
        Each chunk should have: id, content, embedding, url, title, chunk_index
        """
        try:
            points = []
            for chunk in content_chunks:
                points.append(PointStruct(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, chunk['id']).hex,
                    vector=chunk['embedding'],
                    payload={
                        "content": chunk['content'],
                        "url": chunk['url'],
                        "title": chunk['title'],
                        "chunk_index": chunk['chunk_index'],
                        "metadata": chunk.get('metadata', {})
                    }
                ))

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            self.logger.error(f"Error storing embeddings in Qdrant: {str(e)}")
            raise

    def search_similar(self, query_embedding: List[float], top_k: int = 5, page_url: Optional[str] = None) -> List[dict]:
        """
        Search for similar content based on embedding
        If page_url is provided, prioritize results from that page
        """
        try:
            if page_url:
                # Search with filtering for specific page
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    query_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="url",
                                match=models.MatchValue(value=page_url)
                            )
                        ]
                    )
                )
            else:
                # Standard search across all content
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k
                )

            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "content": result.payload["content"],
                    "url": result.payload["url"],
                    "title": result.payload["title"],
                    "chunk_index": result.payload["chunk_index"],
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {})
                })

            return results
        except Exception as e:
            self.logger.error(f"Error searching similar content in Qdrant: {str(e)}")
            return []

    def get_all_documents(self):
        """Retrieve all documents from the collection"""
        try:
            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust as needed
            )

            documents = []
            for record in records:
                documents.append({
                    "id": record.id,
                    "content": record.payload["content"],
                    "url": record.payload["url"],
                    "title": record.payload["title"],
                    "chunk_index": record.payload["chunk_index"],
                    "metadata": record.payload.get("metadata", {})
                })

            return documents
        except Exception as e:
            self.logger.error(f"Error retrieving all documents from Qdrant: {str(e)}")
            return []

    def delete_collection(self):
        """Delete the entire collection (use with caution)"""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as e:
            self.logger.error(f"Error deleting collection from Qdrant: {str(e)}")
            raise