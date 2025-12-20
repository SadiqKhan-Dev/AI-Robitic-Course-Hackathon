from pydantic import BaseModel
from typing import List
from datetime import datetime


class Response(BaseModel):
    """
    Represents the AI agent's response to a user's query.
    """
    id: str  # Unique identifier for the response
    query_id: str  # Reference to the original query
    answer: str  # The AI-generated answer based on book content
    sources: List[str]  # IDs of content chunks used to generate the answer
    confidence: float  # Confidence score of the response (0.0-1.0)
    timestamp: datetime = datetime.now()  # When the response was generated
    fallback_used: bool = False  # Whether the "I don't know" fallback was used