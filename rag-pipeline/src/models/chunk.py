"""Text chunk model."""

import hashlib
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TextChunk(BaseModel):
    """Represents a text chunk ready for embedding."""

    chunk_id: str
    text: str = Field(..., min_length=10)
    source_url: str
    source_title: str = Field(..., max_length=500)
    chunk_index: int = Field(..., ge=0)
    total_chunks: int = Field(..., gt=0)
    token_count: int = Field(..., ge=1)
    char_start: int = Field(..., ge=0)
    char_end: int = Field(..., gt=0)
    metadata: dict = Field(default_factory=dict)

    @field_validator("char_end")
    @classmethod
    def validate_char_range(cls, v: int, info) -> int:
        """Ensure char_end > char_start."""
        char_start = info.data.get("char_start", 0)
        if v <= char_start:
            raise ValueError("char_end must be greater than char_start")
        return v

    @field_validator("chunk_index")
    @classmethod
    def validate_index(cls, v: int, info) -> int:
        """Ensure chunk_index < total_chunks."""
        total = info.data.get("total_chunks", 0)
        if total and v >= total:
            raise ValueError("chunk_index must be less than total_chunks")
        return v

    @classmethod
    def generate_id(cls, url: str, chunk_index: int) -> str:
        """Generate a unique chunk ID.

        Args:
            url: Source URL
            chunk_index: Index of this chunk

        Returns:
            Unique chunk ID string
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        return f"{url_hash}_{chunk_index}"

    @classmethod
    def from_document(
        cls,
        document: "DocumentPage",
        chunks: list[str],
        token_counts: list[int],
        char_positions: list[tuple[int, int]],
    ) -> list["TextChunk"]:
        """Create TextChunk instances from a document.

        Args:
            document: Source document
            chunks: List of text chunks
            token_counts: Token count for each chunk
            char_positions: (start, end) positions for each chunk

        Returns:
            List of TextChunk instances
        """
        url = document.url
        title = document.title
        total = len(chunks)

        return [
            cls(
                chunk_id=cls.generate_id(url, i),
                text=chunk_text,
                source_url=url,
                source_title=title,
                chunk_index=i,
                total_chunks=total,
                token_count=token_counts[i],
                char_start=char_positions[i][0],
                char_end=char_positions[i][1],
                metadata={
                    "doc_type": document.metadata.get("doc_type", "unknown"),
                    "content_hash": document.content_hash,
                },
            )
            for i, chunk_text in enumerate(chunks)
        ]


# Import DocumentPage for type hint (avoid circular import)
from .document import DocumentPage
