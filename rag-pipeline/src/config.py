"""Pipeline configuration and environment variables."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PipelineConfig(BaseModel):
    """Pipeline configuration from environment and config files."""

    # Docusaurus site
    docusaurus_url: str = "https://ai-robitic-course-hackathon.vercel.app/"
    sitemap_url: str = ""

    # Cohere settings
    cohere_api_key: str = ""
    cohere_model: str = "embed-english-v3.0"
    cohere_batch_size: int = 96
    cohere_max_rpm: int = 100

    # Qdrant settings
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "docs-embeddings"

    # Chunking settings
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Concurrency settings
    max_concurrent_requests: int = 5
    request_delay: float = 0.6  # 60s / 100 RPM

    # Storage paths
    data_dir: str = "./data"
    cache_dir: str = "./data/cache"
    state_dir: str = "./data/state"
    log_dir: str = "./data/logs"

    # Logging
    log_level: str = "INFO"

    @model_validator(mode="after")
    def compute_sitemap_url(self):
        """Auto-compute sitemap URL from docusaurus_url."""
        if not self.sitemap_url and self.docusaurus_url:
            base = self.docusaurus_url.rstrip("/")
            self.sitemap_url = f"{base}/sitemap.xml"
        return self

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @model_validator(mode="after")
    def validate_required_fields(self):
        """Ensure required fields are not empty."""
        if not self.cohere_api_key:
            raise ValueError("cohere_api_key is required. Set it in .env file.")
        if not self.qdrant_url:
            raise ValueError("qdrant_url is required. Set it in .env file.")
        if not self.qdrant_api_key:
            raise ValueError("qdrant_api_key is required. Set it in .env file.")
        return self

    @property
    def embedding_dimensions(self) -> int:
        """Return embedding dimensions based on model."""
        # embed-english-v3.0 uses 1024 dimensions
        return 1024

    def get_state_path(self, stage: str) -> Path:
        """Get path for state file for a given stage."""
        return Path(self.state_dir) / f"{stage}_state.json"

    def get_cache_path(self, url_hash: str, ext: str = "txt") -> Path:
        """Get path for cached file."""
        return Path(self.cache_dir) / "extracted" / f"{url_hash}.{ext}"

    def ensure_dirs(self) -> None:
        """Ensure all required directories exist."""
        dirs = [
            self.data_dir,
            self.cache_dir,
            self.state_dir,
            self.log_dir,
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)


def load_config() -> PipelineConfig:
    """Load pipeline configuration from environment."""
    import os
    from dotenv import load_dotenv

    # Set env file path to rag-pipeline directory
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path, override=True)

    # Read from environment directly
    return PipelineConfig(
        cohere_api_key=os.environ.get("COHERE_API_KEY", ""),
        qdrant_url=os.environ.get("QDRANT_URL", ""),
        qdrant_api_key=os.environ.get("QDRANT_API_KEY", ""),
    )
