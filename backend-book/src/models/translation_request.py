from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class TranslationRequest(BaseModel):
    id: Optional[str] = None
    source_content: str = Field(..., max_length=5000 * 10)  # Approx 5000 words
    source_language: str = Field(..., pattern=r'^[a-z]{2,3}$')  # e.g., "en", "es", "fr"
    target_language: str = Field(..., pattern=r'^[a-z]{2,3}$')  # e.g., "en", "es", "fr"
    preserve_formatting: bool = True
    preserve_code_blocks: bool = True
    preserve_technical_terms: bool = True
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    @validator('target_language')
    def validate_target_language_different(cls, v, values):
        if 'source_language' in values and v == values['source_language']:
            raise ValueError('Target language must be different from source language')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "source_content": "Hello, world! This is a sample text.",
                "source_language": "en",
                "target_language": "es",
                "preserve_formatting": True,
                "preserve_code_blocks": True,
                "preserve_technical_terms": True
            }
        }