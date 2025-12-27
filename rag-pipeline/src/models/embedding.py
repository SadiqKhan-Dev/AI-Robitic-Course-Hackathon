"""Embedding and vector record models."""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .chunk import TextChunk


class Embedding(BaseModel):
    """Represents a vector embedding generated from a TextChunk."""

    chunk_id: str
    vector: list[float] = Field(..., min_length=1024, max_length=1024)
    model: str = Field(default="embed-english-v3.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chunk_ref: Optional[TextChunk] = None

    @field_validator("vector")
    @classmethod
    def validate_vector_dimensions(cls, v: list[float]) -> list[float]:
        """Ensure vector has exactly 1024 dimensions."""
        if len(v) != 1024:
            raise ValueError(f"Vector must have 1024 dimensions, got {len(v)}")
        return v

    def to_vector_record(self) -> "VectorRecord":
        """Convert to VectorRecord for Qdrant storage."""
        if self.chunk_ref is None:
            raise ValueError("chunk_ref is required to create VectorRecord")

        return VectorRecord(
            id=self.chunk_id,
            vector=self.vector,
            payload={
                "text": self.chunk_ref.text,
                "url": self.chunk_ref.source_url,
                "title": self.chunk_ref.source_title,
                "chunk_index": self.chunk_ref.chunk_index,
                "total_chunks": self.chunk_ref.total_chunks,
                "token_count": self.chunk_ref.token_count,
                "model": self.model,
                "created_at": self.created_at.isoformat(),
                **self.chunk_ref.metadata,
            },
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "chunk_id": self.chunk_id,
            "vector": self.vector,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "metadata": {
                "text": self.chunk_ref.text if self.chunk_ref else "",
                "url": self.chunk_ref.source_url if self.chunk_ref else "",
                "title": self.chunk_ref.source_title if self.chunk_ref else "",
                "chunk_index": self.chunk_ref.chunk_index if self.chunk_ref else 0,
                "total_chunks": self.chunk_ref.total_chunks if self.chunk_ref else 0,
                "token_count": self.chunk_ref.token_count if self.chunk_ref else 0,
                **(self.chunk_ref.metadata if self.chunk_ref else {}),
            },
        }


class VectorRecord(BaseModel):
    """Represents a vector record for Qdrant storage."""

    id: str
    vector: list[float] = Field(..., min_length=1024, max_length=1024)
    payload: dict = Field(default_factory=dict)

    # Required payload fields (class variable, not a field)
    REQUIRED_PAYLOAD_FIELDS: ClassVar[list[str]] = [
        "text",
        "url",
        "title",
        "chunk_index",
        "total_chunks",
        "token_count",
        "model",
        "created_at",
    ]

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, v: dict) -> dict:
        """Ensure required payload fields are present."""
        missing = [f for f in cls.REQUIRED_PAYLOAD_FIELDS if f not in v]
        if missing:
            raise ValueError(f"Missing required payload fields: {missing}")
        return v

    @field_validator("vector")
    @classmethod
    def validate_vector_dimensions(cls, v: list[float]) -> list[float]:
        """Ensure vector has exactly 1024 dimensions."""
        if len(v) != 1024:
            raise ValueError(f"Vector must have 1024 dimensions, got {len(v)}")
        return v

    def to_qdrant_point(self):
        """Convert to Qdrant PointStruct."""
        from qdrant_client.models import PointStruct

        return PointStruct(
            id=self.id,
            vector=self.vector,
            payload=self.payload,
        )

    @classmethod
    def from_embedding(cls, embedding: Embedding) -> "VectorRecord":
        """Create VectorRecord from Embedding."""
        return embedding.to_vector_record()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "vector": self.vector,
            "payload": self.payload,
        }
