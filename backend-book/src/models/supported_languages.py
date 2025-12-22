from pydantic import BaseModel
from typing import List
from enum import Enum


class TechnicalTermSupport(str, Enum):
    full = "full"
    partial = "partial"
    none = "none"


class SupportedLanguage(BaseModel):
    language_code: str  # e.g., "en", "es", "fr", "ar", "ur"
    language_name: str  # e.g., "English", "Spanish"
    is_enabled: bool = True
    technical_term_support: TechnicalTermSupport = TechnicalTermSupport.full

    class Config:
        json_schema_extra = {
            "example": {
                "language_code": "es",
                "language_name": "Spanish",
                "is_enabled": True,
                "technical_term_support": "full"
            }
        }


class SupportedLanguagesResponse(BaseModel):
    languages: List[SupportedLanguage]

    class Config:
        json_schema_extra = {
            "example": {
                "languages": [
                    {
                        "language_code": "es",
                        "language_name": "Spanish",
                        "is_enabled": True,
                        "technical_term_support": "full"
                    },
                    {
                        "language_code": "fr",
                        "language_name": "French",
                        "is_enabled": True,
                        "technical_term_support": "full"
                    }
                ]
            }
        }