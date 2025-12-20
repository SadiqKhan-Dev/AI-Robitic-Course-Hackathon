from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from src.services.rag_agent_service import RAGAgentService
from src.models.query import Query
from src.models.response import Response
from config.settings import settings
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query")
async def query_endpoint(payload: Dict[str, Any]):
    """
    Submit a question and get a response from book content
    """
    try:
        question = payload.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="question is required")
        
        page_context = payload.get("page_context", None)
        user_id = payload.get("user_id", f"anonymous_{uuid.uuid4()}")
        
        # Create query object
        query_obj = Query(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question=question,
            page_context=page_context
        )
        
        # Generate response using RAG agent
        rag_agent = RAGAgentService()
        response = rag_agent.generate_response(
            query=question,
            user_id=user_id,
            page_context=page_context
        )
        
        # Update response with query ID
        response.query_id = query_obj.id
        
        return {
            "id": response.id,
            "query_id": response.query_id,
            "answer": response.answer,
            "sources": response.sources,
            "confidence": response.confidence,
            "fallback_used": response.fallback_used,
            "timestamp": response.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/query/page")
async def query_page_endpoint(payload: Dict[str, Any]):
    """
    Submit a question with explicit page-level context
    """
    try:
        question = payload.get("question")
        page_url = payload.get("page_url")
        
        if not question:
            raise HTTPException(status_code=400, detail="question is required")
        if not page_url:
            raise HTTPException(status_code=400, detail="page_url is required")
        
        user_id = payload.get("user_id", f"anonymous_{uuid.uuid4()}")
        
        # Create query object
        query_obj = Query(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question=question,
            page_context=page_url
        )
        
        # Generate response using RAG agent with page context
        rag_agent = RAGAgentService()
        response = rag_agent.generate_response(
            query=question,
            user_id=user_id,
            page_context=page_url
        )
        
        # Update response with query ID
        response.query_id = query_obj.id
        
        return {
            "id": response.id,
            "query_id": response.query_id,
            "answer": response.answer,
            "sources": response.sources,
            "confidence": response.confidence,
            "fallback_used": response.fallback_used,
            "timestamp": response.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query page endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Page query processing failed: {str(e)}")