from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import ingest, query, chat
from config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for the floating RAG-powered AI agent that answers questions from book content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Book RAG Agent API", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

logger.info("FastAPI application initialized")