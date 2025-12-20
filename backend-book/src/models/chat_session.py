from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class ChatSession(BaseModel):
    """
    Represents a conversation session between a user and the AI agent.
    """
    id: str  # Unique identifier for the session
    user_id: str  # Identifier for the user
    created_at: datetime = datetime.now()  # When the session was started
    last_interaction: datetime = datetime.now()  # When the last message was exchanged
    context: List[Dict[str, Any]] = []  # Conversation history (messages exchanged)