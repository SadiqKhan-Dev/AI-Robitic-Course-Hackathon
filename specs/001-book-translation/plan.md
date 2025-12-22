# Implementation Plan: Book Translation

**Branch**: `001-book-translation` | **Date**: December 22, 2025 | **Spec**: [link to spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-book-translation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable translation flow using an LLM-based translation agent and integrate translation controls into the book UI (page-level or selection-based) to allow users to translate book content into multiple languages while preserving technical accuracy and structure.

## Technical Context

**Language/Version**: JavaScript/TypeScript for frontend components, Python 3.11 for backend translation services
**Primary Dependencies**: Docusaurus for documentation framework, React for UI components, FastAPI for backend API, OpenAI or similar LLM service for translation
**Storage**: N/A (stateless translation service, temporary in-memory processing)
**Testing**: pytest for backend services, Jest/React Testing Library for frontend components
**Target Platform**: Web browser (integration with Docusaurus book UI)
**Project Type**: Web application (extension to existing Docusaurus frontend with new backend services)
**Performance Goals**: <10 seconds for documents up to 5,000 words (as per success criteria SC-001)
**Constraints**: Must preserve code blocks and technical terms unchanged, meaning-first translation rather than literal, no hallucinated content
**Scale/Scope**: Support for major languages (Urdu, Arabic, Spanish, French) with technical accuracy

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the constitution file, the following gates apply:

1. **Authoring Stack Compliance**: The solution must work within the Docusaurus documentation framework and integrate with the existing authoring workflow.
   - Status: **PASS** - Translation feature will be implemented as a Docusaurus plugin/component that integrates with the existing book UI.

2. **Dependency Constraints**: Translation service must use allowed dependencies from the constitution (FastAPI, OpenAI Agents/ChatKit SDKs, Qdrant, Neon Postgres).
   - Status: **PASS** - Using FastAPI for backend API and LLM service for translation, which aligns with allowed dependencies.

3. **Infrastructure Compatibility**: Solution must be deployable within free-tier infrastructure constraints (Qdrant Free, Neon Serverless).
   - Status: **PASS** - Translation service is stateless and can work within these constraints, though external LLM API costs need consideration.

4. **RAG Chatbot Alignment**: Implementation must follow the specified RAG chatbot stack principles.
   - Status: **RESOLVED** - Translation feature will operate independently from RAG chatbot to maintain separation of concerns. The translation functionality is a UI enhancement that transforms content display, while the RAG chatbot answers questions based on the content.

5. **Free-Tier Infrastructure**: No proprietary or paid services beyond free tiers.
   - Status: **RESOLVED** - Implementation will use a flexible architecture that can work with various LLM providers and include a configuration option to toggle between different services or even an offline translation model for basic functionality.

6. **No Hallucination**: Must ensure no hallucinated content is added during translation.
   - Status: **PASS** - This is a core requirement of the feature (FR-010) and will be implemented with appropriate validation.

## Project Structure

### Documentation (this feature)

```text
specs/001-book-translation/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── translation-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

frontend-book/
├── src/
│   ├── components/
│   │   ├── TranslationToggle/
│   │   ├── TranslationControls/
│   │   └── TranslatedContent/
│   ├── hooks/
│   │   └── useTranslation/
│   └── services/
│       └── translationAPI.js
└── tests/
    ├── unit/
    └── integration/

backend-book/
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── translation_request.py
│   │   └── translation_response.py
│   ├── services/
│   │   └── translation_service.py
│   └── api/
│       └── v1/
│           └── translation.py
└── tests/
    ├── unit/
    └── integration/

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|

## Phase 1 Completion Summary

The following Phase 1 artifacts have been successfully created:

- `research.md` - Resolved all technical unknowns and architecture decisions
- `data-model.md` - Defined entities and relationships for the translation feature
- `quickstart.md` - Provided setup and usage instructions
- `contracts/` - Created API contracts for translation services
- Agent context updated for Qwen with new technology stack
