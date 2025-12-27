"""Document page model for crawled pages."""

from datetime import datetime
from hashlib import sha256
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class DocumentPage(BaseModel):
    """Represents a crawled documentation page."""

    url: str
    title: str = Field(..., max_length=500)
    extracted_text: str = Field(..., min_length=1)
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str = Field(default="")
    metadata: dict = Field(default_factory=dict)

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is a string."""
        return str(v)

    @field_validator("content_hash", mode="before")
    @classmethod
    def compute_hash(cls, v: str, info) -> str:
        """Compute content hash if not provided."""
        if not v:
            extracted_text = info.data.get("extracted_text", "")
            if extracted_text:
                return sha256(extracted_text.encode()).hexdigest()
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: dict) -> dict:
        """Ensure metadata values are strings."""
        return {str(k): str(val) for k, val in v.items()}

    @model_validator(mode="after")
    def validate_text_length(self) -> "DocumentPage":
        """Ensure extracted text is not empty."""
        if not self.extracted_text or not self.extracted_text.strip():
            raise ValueError("extracted_text cannot be empty")
        return self

    def to_cache_file(self) -> tuple[str, dict]:
        """Returns content and metadata for caching.

        Returns:
            Tuple of (text_content, metadata_dict)
        """
        return (
            self.extracted_text,
            {
                "url": self.url,
                "title": self.title,
                "crawled_at": self.crawled_at.isoformat(),
                "content_hash": self.content_hash,
                "metadata": self.metadata,
            },
        )

    @classmethod
    def from_cache(cls, text_content: str, metadata: dict) -> "DocumentPage":
        """Create a DocumentPage from cached files.

        Args:
            text_content: The extracted text content
            metadata: The metadata dictionary

        Returns:
            DocumentPage instance
        """
        return cls(
            url=metadata.get("url", ""),
            title=metadata.get("title", ""),
            extracted_text=text_content,
            crawled_at=datetime.fromisoformat(metadata.get("crawled_at", datetime.utcnow().isoformat())),
            content_hash=metadata.get("content_hash", ""),
            metadata=metadata.get("metadata", {}),
        )

    def get_url_hash(self) -> str:
        """Get a short hash for this URL."""
        return sha256(self.url.encode()).hexdigest()[:16]
