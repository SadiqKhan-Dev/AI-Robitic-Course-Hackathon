from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class BookContent(BaseModel):
    """
    Represents a chunk of book content that has been processed and embedded for retrieval.
    """
    id: str  # Unique identifier for the content chunk
    url: str  # The source URL from which this content was extracted
    title: str  # The title of the page/chapter this content belongs to
    content: str  # The actual text content of the chunk
    embedding: List[float]  # Vector embedding representation of the content
    chunk_index: int  # Position of this chunk within the original document
    metadata: Optional[Dict] = {}  # Additional metadata (author, date, etc.)