"""State management for resumable pipeline operations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, TypeVar

import structlog
from pydantic import BaseModel, Field

from ..config import PipelineConfig

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class BaseState(BaseModel, Generic[T]):
    """Base class for state tracking."""

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        data = self.model_dump()
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> T:
        """Create from dict."""
        if "last_updated" in data and isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class CrawlState(BaseState):
    """Tracks crawling progress for resumability."""

    urls_discovered: list[str] = Field(default_factory=list)
    urls_completed: list[str] = Field(default_factory=list)
    urls_failed: dict[str, str] = Field(default_factory=dict)
    total_pages: int = 0
    completed_pages: int = 0

    def is_completed(self, url: str) -> bool:
        """Check if URL has been crawled."""
        return url in self.urls_completed

    def mark_completed(self, url: str):
        """Mark URL as completed."""
        if url not in self.urls_completed:
            self.urls_completed.append(url)
            self.completed_pages += 1
            self.last_updated = datetime.utcnow()

    def mark_failed(self, url: str, error: str):
        """Mark URL as failed with error message."""
        self.urls_failed[url] = error
        self.last_updated = datetime.utcnow()

    def get_pending_urls(self) -> list[str]:
        """Get URLs that need to be crawled."""
        completed_set = set(self.urls_completed)
        failed_set = set(self.urls_failed.keys())
        return [
            url for url in self.urls_discovered
            if url not in completed_set and url not in failed_set
        ]


class EmbedState(BaseState):
    """Tracks embedding generation progress."""

    chunks_processed: list[str] = Field(default_factory=list)
    chunks_failed: dict[str, str] = Field(default_factory=dict)
    total_chunks: int = 0
    completed_chunks: int = 0
    batch_size: int = 96

    def is_processed(self, chunk_id: str) -> bool:
        """Check if chunk has been embedded."""
        return chunk_id in self.chunks_processed

    def mark_processed(self, chunk_ids: list[str]):
        """Mark chunks as processed (batch)."""
        self.chunks_processed.extend(chunk_ids)
        self.completed_chunks += len(chunk_ids)
        self.last_updated = datetime.utcnow()

    def mark_failed(self, chunk_id: str, error: str):
        """Mark chunk as failed."""
        self.chunks_failed[chunk_id] = error
        self.last_updated = datetime.utcnow()


class UploadState(BaseState):
    """Tracks vector upload progress to Qdrant."""

    vectors_uploaded: list[str] = Field(default_factory=list)
    vectors_failed: dict[str, str] = Field(default_factory=dict)
    total_vectors: int = 0
    completed_vectors: int = 0
    batch_size: int = 100

    def is_uploaded(self, vector_id: str) -> bool:
        """Check if vector has been uploaded."""
        return vector_id in self.vectors_uploaded

    def mark_uploaded(self, vector_ids: list[str]):
        """Mark vectors as uploaded (batch)."""
        self.vectors_uploaded.extend(vector_ids)
        self.completed_vectors += len(vector_ids)
        self.last_updated = datetime.utcnow()

    def mark_failed(self, vector_id: str, error: str):
        """Mark vector as failed."""
        self.vectors_failed[vector_id] = error
        self.last_updated = datetime.utcnow()


class StateManager:
    """Manages state persistence for pipeline stages."""

    def __init__(self, config: PipelineConfig):
        """Initialize state manager.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.states: dict[str, BaseState] = {}

    def get_crawl_state(self) -> CrawlState:
        """Get or create crawl state."""
        if "crawl" not in self.states:
            self.states["crawl"] = self._load_state("crawl", CrawlState())
        return self.states["crawl"]

    def get_embed_state(self) -> EmbedState:
        """Get or create embed state."""
        if "embed" not in self.states:
            self.states["embed"] = self._load_state("embed", EmbedState())
        return self.states["embed"]

    def get_upload_state(self) -> UploadState:
        """Get or create upload state."""
        if "upload" not in self.states:
            self.states["upload"] = self._load_state("upload", UploadState())
        return self.states["upload"]

    def save_state(self, stage: str):
        """Save state for a given stage.

        Args:
            stage: Stage name (crawl, embed, upload)
        """
        if stage not in self.states:
            return

        state = self.states[stage]
        state_path = self.config.get_state_path(stage)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state.to_dict()))
        logger.debug("state_saved", stage=stage)

    def _load_state(self, stage: str, default: BaseState) -> BaseState:
        """Load state from file or return default.

        Args:
            stage: Stage name
            default: Default state if file not found

        Returns:
            Loaded or default state
        """
        state_path = self.config.get_state_path(stage)
        if state_path.exists():
            try:
                data = json.loads(state_path.read_text())
                state_class = type(default)
                return state_class.from_dict(data)
            except Exception as e:
                logger.warning("state_load_failed", stage=stage, error=str(e))
        return default

    def reset_state(self, stage: str):
        """Reset state for a given stage.

        Args:
            stage: Stage name
        """
        if stage in self.states:
            del self.states[stage]

        state_path = self.config.get_state_path(stage)
        if state_path.exists():
            state_path.unlink()
            logger.info("state_reset", stage=stage)

    def clear_all_states(self):
        """Clear all pipeline states."""
        for stage in ["crawl", "embed", "upload"]:
            self.reset_state(stage)
        logger.info("all_states_cleared")
