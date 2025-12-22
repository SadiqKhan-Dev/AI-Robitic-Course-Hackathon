from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TranslationResponse(BaseModel):
    id: str
    original_request_id: str
    translated_content: str
    detected_technical_elements: List[str] = []
    translation_quality_score: Optional[float] = None  # 0-100 confidence score
    processing_time_ms: int
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "tr_1234567890",
                "original_request_id": "req_0987654321",
                "translated_content": "Hola, mundo! Esta es una muestra de texto.",
                "detected_technical_elements": ["world", "sample"],
                "translation_quality_score": 95.5,
                "processing_time_ms": 1250,
                "timestamp": "2023-10-01T12:00:00Z"
            }
        }