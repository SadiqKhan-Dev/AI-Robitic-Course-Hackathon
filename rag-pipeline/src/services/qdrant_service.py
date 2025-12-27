"""Qdrant Vector Database Service for RAG Pipeline."""
import os
import sys
from pathlib import Path
from typing import Any

import yaml
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SearchRequest,
    VectorParams,
)

# Add rag-pipeline to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self, config_path: str = None):
        """Initialize Qdrant service with config."""
        # Load config
        if config_path is None:
            config_path = PROJECT_ROOT / "config.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["qdrant"]

        # Initialize client
        self.client = QdrantClient(
            url=self.config["url"],
            api_key=self.config["api_key"],
            timeout=60.0,
        )

        self.collection_name = self.config["collection_name"]
        self.vector_size = self.config.get("vector_size", 768)

    def ensure_collection(self, recreate: bool = False) -> bool:
        """Ensure collection exists, optionally recreate."""
        try:
            self.client.get_collection(self.collection_name)
            if recreate:
                self.client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            else:
                print(f"Collection already exists: {self.collection_name}")
                return True
        except Exception:
            pass  # Collection doesn't exist

        # Create collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created collection: {self.collection_name}")
        return True

    def search(
        self, query_vector: list, top_k: int = 5, score_threshold: float = 0.5
    ) -> list[dict]:
        """Search for similar vectors."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]

    def search_by_text(
        self, query_text: str, embedding: list, top_k: int = 5
    ) -> list[dict]:
        """Search by text query using pre-computed embedding."""
        return self.search(embedding, top_k=top_k)

    def get_all_documents(self, limit: int = 100) -> list[dict]:
        """Retrieve all documents from collection."""
        points = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )[0]

        return [
            {
                "id": point.id,
                "payload": point.payload,
            }
            for point in points
        ]

    def get_collection_info(self) -> dict:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        count = self.client.count(self.collection_name, exact=True)

        return {
            "status": str(info.status),
            "vectors_count": info.vectors_count,
            "points_count": count.count,
            "vector_size": self.vector_size,
        }

    def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False


def get_qdrant_service(config_path: str = None) -> QdrantService:
    """Factory function to get Qdrant service instance."""
    return QdrantService(config_path)


if __name__ == "__main__":
    # Test the service
    service = get_qdrant_service()
    info = service.get_collection_info()
    print(f"Collection Info: {info}")
