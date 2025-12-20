from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.models.chat_session import ChatSession
from src.services.rag_agent_service import RAGAgentService
from config.settings import settings
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for chat sessions (in production, use a database)
chat_sessions: Dict[str, ChatSession] = {}


@router.post("/chat/start")
async def start_chat_session(payload: Dict[str, str]):
    """
    Start a new chat session
    """
    try:
        user_id = payload.get("user_id", f"anonymous_{uuid.uuid4()}")
        
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=user_id
        )
        
        chat_sessions[session_id] = chat_session
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": chat_session.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error in start chat session endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat session: {str(e)}")


@router.post("/chat/{session_id}")
async def chat_message(session_id: str, payload: Dict[str, Any]):
    """
    Send a message in a chat session
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        question = payload.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="question is required")
        
        page_context = payload.get("page_context", None)
        
        # Get the session
        chat_session = chat_sessions[session_id]
        
        # Generate response using RAG agent
        rag_agent = RAGAgentService()
        response = rag_agent.generate_response(
            query=question,
            user_id=chat_session.user_id,
            page_context=page_context
        )
        
        # Update response with query ID (using a simple approach for chat)
        response.query_id = str(uuid.uuid4())
        
        # Add to session context (limit context size to prevent memory issues)
        chat_session.context.append({
            "type": "query",
            "content": question,
            "id": response.query_id
        })
        chat_session.context.append({
            "type": "response",
            "content": response.answer,
            "id": response.id,
            "sources": response.sources,
            "confidence": response.confidence,
            "fallback_used": response.fallback_used
        })
        
        # Limit context to last 10 exchanges to manage memory
        if len(chat_session.context) > 20:  # 10 Q&A pairs
            chat_session.context = chat_session.context[-20:]
        
        # Update last interaction time
        chat_session.last_interaction = response.timestamp
        
        return {
            "session_id": session_id,
            "query_id": response.query_id,
            "response_id": response.id,
            "answer": response.answer,
            "sources": response.sources,
            "confidence": response.confidence,
            "fallback_used": response.fallback_used,
            "timestamp": response.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat message endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat message processing failed: {str(e)}")


@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """
    Get the history of a chat session
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        chat_session = chat_sessions[session_id]
        
        return {
            "session_id": session_id,
            "user_id": chat_session.user_id,
            "history": chat_session.context,
            "created_at": chat_session.created_at.isoformat(),
            "last_interaction": chat_session.last_interaction.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get chat history endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")