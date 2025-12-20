from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Query(BaseModel):
    """
    Represents a user's question or query to the RAG system.
    """
    id: str  # Unique identifier for the query
    user_id: str  # Identifier for the user making the query
    question: str  # The natural language question from the user
    timestamp: datetime = datetime.now()  # When the query was made
    page_context: Optional[str] = None  # URL of the current page when query was made