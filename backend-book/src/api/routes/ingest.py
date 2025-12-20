from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from src.services.ingestion_service import IngestionService
from config.settings import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest")
async def ingest_content(payload: Dict[str, str]):
    """
    Trigger content ingestion from a sitemap
    """
    try:
        sitemap_url = payload.get("sitemap_url")
        if not sitemap_url:
            raise HTTPException(status_code=400, detail="sitemap_url is required")
        
        ingestion_service = IngestionService()
        result = ingestion_service.ingest_from_sitemap(sitemap_url)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/ingest/stats")
async def get_ingestion_stats():
    """
    Get statistics about the ingested content
    """
    try:
        ingestion_service = IngestionService()
        stats = ingestion_service.get_ingested_content_stats()
        
        if "status" in stats and stats["status"] == "error":
            raise HTTPException(status_code=500, detail=stats["message"])
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ingest stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")