"""FastAPI Backend for AI Book Chatbot Widget."""
import sys
from pathlib import Path
from typing import List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add rag-pipeline to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load config
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title="AI Book Chatbot API",
    description="RAG-powered chatbot for AI Robotics Book",
    version="1.0.0"
)

# Add CORS middleware properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent (lazy initialization)
_agent = None


def get_agent():
    """Get or create RAG agent."""
    global _agent
    if _agent is None:
        from src.agents.rag_agent import get_rag_agent
        _agent = get_rag_agent(str(CONFIG_PATH))
    return _agent


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    documents_count: int


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {"message": "AI Book Chatbot API is running", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check system health."""
    try:
        from src.services.qdrant_service import QdrantService
        qdrant = QdrantService(str(CONFIG_PATH))
        info = qdrant.get_collection_info()
        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            documents_count=info.get("points_count", 0)
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            qdrant_connected=False,
            documents_count=0
        )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Process chat message and return response."""
    try:
        agent = get_agent()
        result = agent.generate_response(request.message)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            success=True
        )
    except ValueError as e:
        # Missing API key
        return ChatResponse(
            answer="",
            sources=[],
            success=False,
            error=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", tags=["Search"])
async def search_documents(query: str, limit: int = 5):
    """Search documents in knowledge base."""
    try:
        agent = get_agent()
        context = agent.search_knowledge_base(query)
        return {"results": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get collection statistics."""
    try:
        from src.services.qdrant_service import QdrantService
        from src.services.embedding_service import EmbeddingService

        qdrant = QdrantService(str(CONFIG_PATH))
        info = qdrant.get_collection_info()

        embed_service = EmbeddingService(str(CONFIG_PATH))

        return {
            "collection": config["qdrant"]["collection_name"],
            "documents": info.get("points_count", 0),
            "vector_size": info.get("vector_size", 0),
            "embedding_model": embed_service.model_name,
            "llm_model": config["gemini"]["model"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
