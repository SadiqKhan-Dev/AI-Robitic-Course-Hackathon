import re
import asyncio
import logging
import time
from typing import List, Tuple, Dict
from datetime import datetime
from ..models.translation_request import TranslationRequest
from ..models.translation_response import TranslationResponse
from ..models.supported_languages import SupportedLanguage, TechnicalTermSupport
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        # Initialize LLM client (OpenAI or configurable provider)
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("LLM_MODEL_NAME", "gpt-4-turbo")
        
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required")
        
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        
        # Supported languages
        self.supported_languages = [
            SupportedLanguage(language_code="en", language_name="English", is_enabled=True),
            SupportedLanguage(language_code="es", language_name="Spanish", is_enabled=True),
            SupportedLanguage(language_code="fr", language_name="French", is_enabled=True),
            SupportedLanguage(language_code="ar", language_name="Arabic", is_enabled=True),
            SupportedLanguage(language_code="ur", language_name="Urdu", is_enabled=True),
        ]
        
        # Regex patterns for detecting technical elements
        self.code_block_pattern = r'(```[\s\S]*?```|`[^`\n]*`)'
        self.inline_code_pattern = r'`[^`\n]*`'
        self.file_path_pattern = r'([/\w\-.]+\.[\w]+)'
        self.command_pattern = r'(```[\s\S]*?```|`[^`\n]*`)'
        
    async def get_supported_languages(self) -> List[SupportedLanguage]:
        """Return the list of supported languages."""
        return self.supported_languages
    
    async def validate_language_support(self, source_lang: str, target_lang: str) -> bool:
        """Validate if both source and target languages are supported."""
        source_supported = any(lang.language_code == source_lang and lang.is_enabled 
                              for lang in self.supported_languages)
        target_supported = any(lang.language_code == target_lang and lang.is_enabled 
                              for lang in self.supported_languages)
        return source_supported and target_supported
    
    async def extract_technical_elements(self, content: str) -> List[str]:
        """Extract technical elements like code blocks, file paths, commands, and technical terms."""
        elements = []

        # Extract code blocks (```...``` and `...`)
        code_blocks = re.findall(self.code_block_pattern, content)
        elements.extend(code_blocks)

        # Extract file paths (more comprehensive pattern)
        file_path_pattern = r'(?:\.{0,2}/)?[\w\-_/\\]+(?:\.[\w]+)+'
        file_paths = re.findall(file_path_pattern, content)
        # Filter to likely file paths (not just any word with dots)
        file_paths = [path for path in file_paths if '.' in path.split('/')[-1].split('\\')[-1]]
        elements.extend(file_paths)

        # Extract technical terms (commands, function names, etc.) - more comprehensive
        # Look for patterns like: function_name(), command-line commands, technical acronyms
        technical_pattern = r'\b(?:[A-Z]{2,}|[a-z]+(?:[A-Z][a-z]*)+|[a-z_][a-zA-Z0-9_]*\(\)|[a-z\-]+-[a-z\-]+)\b'
        technical_terms = re.findall(technical_pattern, content)
        elements.extend(technical_terms)

        # Remove duplicates while preserving order
        unique_elements = []
        seen = set()
        for element in elements:
            if element not in seen:
                seen.add(element)
                unique_elements.append(element)

        return unique_elements
    
    async def preserve_technical_elements(self, content: str) -> Tuple[str, Dict[str, str]]:
        """
        Replace technical elements with placeholders to preserve them during translation.
        Returns the content with placeholders and a mapping of placeholders to original elements.
        """
        placeholders = {}
        preserved_content = content
        
        # Extract and replace code blocks
        code_blocks = re.findall(self.code_block_pattern, content)
        for i, block in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            placeholders[placeholder] = block
            preserved_content = preserved_content.replace(block, placeholder, 1)
        
        # Extract and replace file paths
        file_paths = re.findall(self.file_path_pattern, preserved_content)
        # Filter to likely file paths
        file_paths = [path for path in file_paths if '.' in path.split('/')[-1]]
        for i, path in enumerate(file_paths):
            placeholder = f"__FILE_PATH_{i}__"
            placeholders[placeholder] = path
            preserved_content = preserved_content.replace(path, placeholder, 1)
        
        return preserved_content, placeholders
    
    async def restore_technical_elements(self, content: str, placeholders: Dict[str, str]) -> str:
        """Restore technical elements from placeholders."""
        restored_content = content
        for placeholder, original in placeholders.items():
            restored_content = restored_content.replace(placeholder, original)
        return restored_content

    async def validate_preserved_elements(self, original_content: str, final_content: str) -> Dict[str, any]:
        """Validate that technical elements were properly preserved during translation."""
        # Extract technical elements from original content
        original_elements = await self.extract_technical_elements(original_content)

        # Extract technical elements from final content
        final_elements = await self.extract_technical_elements(final_content)

        # Compare to ensure all original elements are preserved
        missing_elements = []
        preserved_elements = []

        for element in original_elements:
            if element in final_content:
                preserved_elements.append(element)
            else:
                missing_elements.append(element)

        # Calculate preservation rate
        total_elements = len(original_elements)
        preserved_count = len(preserved_elements)
        preservation_rate = (preserved_count / total_elements * 100) if total_elements > 0 else 100

        return {
            "preservation_rate": preservation_rate,
            "total_elements": total_elements,
            "preserved_elements": preserved_elements,
            "missing_elements": missing_elements,
            "is_valid": preservation_rate >= 95  # 95% threshold for validation
        }
    
    async def translate_content(self, request: TranslationRequest) -> TranslationResponse:
        """Translate content while preserving technical elements."""
        start_time = time.time()
        start_datetime = datetime.now()

        # Performance monitoring: log initial request details
        logger.info(f"Starting translation request: {request.id}, content length: {len(request.source_content)} chars")

        # Validate language support
        if not await self.validate_language_support(request.source_language, request.target_language):
            raise ValueError(f"Unsupported language combination: {request.source_language} -> {request.target_language}")

        # Extract technical elements to preserve
        extract_start = time.time()
        technical_elements = await self.extract_technical_elements(request.source_content)
        extract_duration = time.time() - extract_start

        # Preserve technical elements with placeholders
        preserve_start = time.time()
        preserved_content, placeholders = await self.preserve_technical_elements(request.source_content)
        preserve_duration = time.time() - preserve_start

        # Prepare the translation prompt
        prompt = self._build_translation_prompt(
            preserved_content,
            request.source_language,
            request.target_language,
            request.preserve_formatting,
            request.preserve_technical_terms
        )

        try:
            # Call the LLM for translation
            llm_start = time.time()
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the user's content accurately while preserving the meaning and structure. Never translate code blocks, file names, or technical terms that should remain unchanged."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
            )
            llm_duration = time.time() - llm_start

            # Extract the translated content
            translated_content = response.choices[0].message.content

            if not translated_content:
                raise ValueError("Translation service returned empty content")

            # Restore technical elements
            restore_start = time.time()
            final_content = await self.restore_technical_elements(translated_content, placeholders)
            restore_duration = time.time() - restore_start

            # Validate preservation of technical elements
            validation_result = await self.validate_preserved_elements(request.source_content, final_content)

            # Log preservation validation results
            logger.info(f"Translation preservation validation: {validation_result}")

            # Calculate quality score based on preservation rate and other factors
            preservation_score = validation_result["preservation_rate"]

            # Calculate length similarity (another quality indicator)
            original_length = len(request.source_content)
            final_length = len(final_content)
            length_similarity = 100 - abs(original_length - final_length) / max(original_length, 1) * 100
            length_score = max(0, min(100, length_similarity))

            # Calculate final quality score (weighted average)
            # Preservation is most important (70%), length similarity (30%)
            final_quality_score = (preservation_score * 0.7) + (length_score * 0.3)

            # Calculate processing time
            total_processing_time = time.time() - start_time
            processing_time_ms = int(total_processing_time * 1000)

            # Performance monitoring: log detailed timing
            logger.info(
                f"Translation completed: id={request.id}, "
                f"total_time={processing_time_ms}ms, "
                f"extract_time={int(extract_duration * 1000)}ms, "
                f"preserve_time={int(preserve_duration * 1000)}ms, "
                f"llm_time={int(llm_duration * 1000)}ms, "
                f"restore_time={int(restore_duration * 1000)}ms, "
                f"quality_score={final_quality_score}, "
                f"preserved_elements={len(technical_elements)}"
            )

            # Create and return the response
            return TranslationResponse(
                id=f"tr_{int(datetime.now().timestamp())}",
                original_request_id=f"req_{int(datetime.now().timestamp())}",
                translated_content=final_content,
                detected_technical_elements=technical_elements,
                translation_quality_score=round(final_quality_score, 2),
                processing_time_ms=processing_time_ms,
                timestamp=start_datetime
            )

        except openai.APIError as e:
            logger.error(f"OpenAI API error during translation: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during translation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during translation: {str(e)}")
            raise
    
    async def translate_selection(self, full_content: str, selection_start: int, selection_end: int, 
                                 source_language: str, target_language: str) -> Tuple[str, str]:
        """
        Translate a selected portion of content while maintaining context with the surrounding document.
        Returns both the translated selection and the full content with only the selection translated.
        """
        # Extract the selected portion
        selected_text = full_content[selection_start:selection_end]
        
        # Create a request for the selected text
        request = TranslationRequest(
            source_content=selected_text,
            source_language=source_language,
            target_language=target_language,
            preserve_formatting=True,
            preserve_code_blocks=True,
            preserve_technical_terms=True
        )
        
        # Translate the selected portion
        translation_response = await self.translate_content(request)
        
        # Replace the original selected portion with the translated one
        context_preserved_content = (
            full_content[:selection_start] + 
            translation_response.translated_content + 
            full_content[selection_end:]
        )
        
        return translation_response.translated_content, context_preserved_content
    
    def _build_translation_prompt(self, content: str, source_lang: str, target_lang: str, 
                                preserve_formatting: bool, preserve_technical_terms: bool) -> str:
        """Build the appropriate prompt based on requirements."""
        prompt_parts = [
            f"Translate the following content from {source_lang} to {target_lang}.",
        ]
        
        if preserve_formatting:
            prompt_parts.append("Preserve the original formatting, structure, and document hierarchy.")
        
        if preserve_technical_terms:
            prompt_parts.append(
                "Do not translate code blocks, file names, technical terms, or commands. "
                "Keep them exactly as they appear in the original text."
            )
        else:
            prompt_parts.append(
                "Translate technical terms appropriately for the target language, "
                "but keep code blocks and file names unchanged."
            )
        
        prompt_parts.append(
            "Focus on meaning-first translation rather than word-for-word translation. "
            "Ensure the translated content maintains the same semantic meaning as the original."
        )
        
        prompt_parts.append("\nContent to translate:")
        prompt_parts.append(content)
        
        return "\n".join(prompt_parts)