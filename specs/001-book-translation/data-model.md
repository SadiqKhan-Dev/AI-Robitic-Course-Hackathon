# Data Model: Book Translation Feature

## Entities

### Translation Request
**Description**: Represents a user's request to translate content from a source language to a target language

**Fields**:
- `id` (string): Unique identifier for the translation request
- `source_content` (string): The original content to be translated
- `source_language` (string): The language of the original content (e.g., "en")
- `target_language` (string): The language to translate to (e.g., "es", "fr", "ar", "ur")
- `preserve_formatting` (boolean): Whether to maintain document structure during translation
- `preserve_code_blocks` (boolean): Whether code blocks should remain unchanged
- `preserve_technical_terms` (boolean): Whether technical terms should be preserved/localized appropriately
- `user_id` (string, optional): Identifier of the requesting user (for analytics)
- `timestamp` (datetime): When the request was made

**Validation Rules**:
- `source_language` and `target_language` must be in the supported languages list
- `source_content` must not exceed 5,000 words (per success criteria SC-001)
- `target_language` must be different from `source_language`

### Translated Content
**Description**: The output of the translation process, maintaining structure and technical elements

**Fields**:
- `id` (string): Unique identifier for the translated content
- `original_request_id` (string): Reference to the Translation Request
- `translated_content` (string): The translated content with preserved elements
- `detected_technical_elements` (array): List of preserved technical elements (code blocks, file names, etc.)
- `translation_quality_score` (number): Confidence score for the translation quality
- `processing_time_ms` (number): Time taken to process the translation
- `timestamp` (datetime): When the translation was completed

**Validation Rules**:
- `translated_content` should maintain the same structural elements as the original
- At least 95% of code blocks should remain unchanged (per success criteria SC-002)
- `processing_time_ms` should be under 10,000ms for content up to 5,000 words (per success criteria SC-001)

### Supported Languages
**Description**: Collection of languages the system can translate to

**Fields**:
- `language_code` (string): Standard language code (e.g., "en", "es", "fr", "ar", "ur")
- `language_name` (string): Full name of the language (e.g., "English", "Spanish")
- `is_enabled` (boolean): Whether this language is currently supported
- `technical_term_support` (string): Level of technical term support ("full", "partial", "none")

**Validation Rules**:
- Must include at least 4 major languages as specified in FR-004
- `language_code` must follow ISO 639-1 or 639-3 standard
- At least "es", "fr", "ar", "ur" must be enabled to meet feature requirements

## Relationships

- `Translation Request` → `Translated Content`: One-to-one relationship (each request produces one translated output)
- `Translation Request` → `Supported Languages`: Many-to-one (requests target a supported language)

## State Transitions

### Translation Request
- `PENDING` → `PROCESSING`: When translation service starts processing
- `PROCESSING` → `COMPLETED`: When translation is finished successfully
- `PROCESSING` → `FAILED`: When translation encounters an error
- `PENDING` → `FAILED`: When request validation fails