from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    COHERE_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_HOST: str
    GEMINI_API_KEY: Optional[str] = None  # Optional, as we might use other providers
    
    # Book configuration
    BOOK_SITEMAP_URL: str
    
    # Application settings
    APP_NAME: str = "Book RAG Agent"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Embedding settings
    EMBEDDING_MODEL: str = "embed-multilingual-v3.0"
    EMBEDDING_DIMENSION: int = 1024  # Cohere embed-multilingual-v3.0 has 1024 dimensions
    
    # Qdrant settings
    QDRANT_COLLECTION_NAME: str = "book_content"
    
    # Text chunking settings
    CHUNK_SIZE: int = 512  # tokens
    CHUNK_OVERLAP: float = 0.2  # 20% overlap
    
    # Retrieval settings
    TOP_K: int = 5  # Number of chunks to retrieve
    MIN_RELEVANCE_SCORE: float = 0.3  # Minimum relevance score for inclusion
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100  # requests per minute per IP
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()