from fastapi import APIRouter, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
import logging
from pydantic import BaseModel
from ...models.translation_request import TranslationRequest
from ...models.translation_response import TranslationResponse
from ...models.supported_languages import SupportedLanguagesResponse
from ...services.translation_service import TranslationService

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the translation service
translation_service = TranslationService()


@router.post("/translate", response_model=TranslationResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def translate_content(request: TranslationRequest):
    """
    Translates content from source language to target language while preserving technical elements.
    """
    try:
        # Validate content length (should not exceed 5000 words - roughly 25000 chars)
        if len(request.source_content) > 25000:  # Approximate 5000 words
            raise HTTPException(
                status_code=400,
                detail="Content exceeds maximum length of approximately 5000 words"
            )

        # Perform the translation
        result = await translation_service.translate_content(request)
        return result

    except ValueError as e:
        logger.error(f"Validation error during translation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Translation service error")


@router.get("/supported-languages", response_model=SupportedLanguagesResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP (lighter operation)
async def get_supported_languages():
    """
    Retrieves the list of supported languages for translation.
    """
    try:
        languages = await translation_service.get_supported_languages()
        return SupportedLanguagesResponse(languages=languages)
    except Exception as e:
        logger.error(f"Error retrieving supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving supported languages")


class SelectionTranslationRequest(BaseModel):
    full_content: str
    selection_start: int
    selection_end: int
    source_language: str
    target_language: str


@router.post("/translate-selection", response_model=TranslationResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def translate_selection(request: SelectionTranslationRequest):
    """
    Translates a selected portion of content while maintaining context with the surrounding document.
    """
    try:
        # Validate selection range
        if (request.selection_start < 0 or
            request.selection_end > len(request.full_content) or
            request.selection_start >= request.selection_end):
            raise HTTPException(
                status_code=400,
                detail="Invalid selection range"
            )

        # Perform the selection translation
        translated_selection, context_preserved_content = await translation_service.translate_selection(
            request.full_content,
            request.selection_start,
            request.selection_end,
            request.source_language,
            request.target_language
        )

        # Create a response with the translated selection
        from datetime import datetime
        import uuid

        return TranslationResponse(
            id=f"tr_{int(datetime.now().timestamp())}",
            original_request_id=f"req_{int(uuid.uuid4())}",
            translated_content=context_preserved_content,  # Full content with only selection translated
            detected_technical_elements=[],  # TODO: Implement technical element detection for selection
            translation_quality_score=95.0,  # Placeholder
            processing_time_ms=0,  # Placeholder
            timestamp=datetime.now()
        )

    except ValueError as e:
        logger.error(f"Validation error during selection translation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Selection translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Selection translation service error")