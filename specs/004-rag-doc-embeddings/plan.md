# Implementation Plan: RAG Documentation Embeddings Pipeline

**Branch**: `004-rag-doc-embeddings` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-rag-doc-embeddings/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a RAG ingestion pipeline that crawls the deployed Docusaurus documentation site (https://ai-robitic-course-hackathon.vercel.app/), extracts and cleans text content, chunks it into semantic units, generates vector embeddings using Cohere's embedding API, and stores them in Qdrant vector database for future retrieval. The pipeline must be reliable, resumable on failure, and handle rate limits gracefully while maintaining metadata traceability from source URLs to stored vectors.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- **Web Scraping**: requests, beautifulsoup4 (HTML parsing), lxml (fast parsing)
- **Embeddings**: cohere (official Python SDK)
- **Vector DB**: qdrant-client (official Python client)
- **Text Processing**: tiktoken (OpenAI tokenizer for accurate token counting), langchain-text-splitters or similar chunking library
- **Configuration**: python-dotenv (env management), pydantic (config validation)
- **Async/Concurrency**: NEEDS CLARIFICATION (asyncio vs threading for concurrent API calls)
- **Logging**: structlog or standard logging module

**Storage**:
- Vector storage: Qdrant Cloud (free tier: 1GB storage, 100 req/min)
- Intermediate storage: Local filesystem for state tracking (JSON or SQLite for resume capability)
- NEEDS CLARIFICATION: Should we cache crawled HTML or extracted text for debugging?

**Testing**: pytest with fixtures for mocked API responses (Cohere, Qdrant), integration tests against Qdrant test instance

**Target Platform**: Development/CI environment (Linux/Windows/macOS compatible), scripts run as CLI tools

**Project Type**: Single project (Python CLI scripts with library structure)

**Performance Goals**:
- Crawl 100-200 pages in <10 minutes
- Embed 500-1000 chunks in <20 minutes (with Cohere rate limits)
- Upload to Qdrant in <5 minutes
- Total pipeline: <30 minutes for typical documentation site

**Constraints**:
- Cohere API: NEEDS CLARIFICATION (Free tier rate limits - need to research)
- Qdrant Cloud free tier: 1GB storage, ~100 req/min
- Must implement exponential backoff for rate limits
- Must support resumable operations (state checkpointing)
- Memory efficient: stream processing where possible, batch API calls

**Scale/Scope**:
- Target: 100-200 documentation pages
- Expected chunks: 1000-3000 text chunks
- Embedding dimensions: NEEDS CLARIFICATION (Cohere model - likely 768 or 1024 dimensions)
- Metadata per vector: URL, chunk text, position, page title (~500 bytes avg)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Project constitution is currently a template with placeholder principles. Assuming standard software engineering best practices apply:

### Library-First Design ✅
- RAG pipeline will be structured as modular libraries (crawling, chunking, embedding, storage)
- Each module independently testable and documented
- Clear separation of concerns

### CLI Interface ✅
- Scripts expose functionality via CLI with args/stdin
- Output formats: JSON for machine consumption, human-readable logs
- Exit codes for success/failure

### Test-First Approach ✅
- TDD cycle: Write tests → Implement → Pass tests
- Unit tests for each module
- Integration tests for full pipeline
- Contract tests for external APIs (mocked)

### Integration Testing ✅
- Full pipeline integration tests
- Cohere API integration (with mocks)
- Qdrant client integration (with test instance)

### Observability ✅
- Structured logging throughout pipeline
- Progress tracking and metrics
- Error tracking with context

### Simplicity ✅
- Start with synchronous processing, optimize if needed
- Use standard libraries where possible
- No premature abstractions

**Constitution Compliance**: ✅ PASS - No violations detected. Design follows modular, testable, observable patterns.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
rag-pipeline/                    # New directory for RAG ingestion pipeline
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration and environment variables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py          # DocumentPage model
│   │   ├── chunk.py             # TextChunk model
│   │   └── embedding.py         # Embedding and VectorRecord models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py           # Web crawling and URL discovery
│   │   ├── extractor.py         # HTML content extraction and cleaning
│   │   ├── chunker.py           # Text chunking logic
│   │   ├── embedder.py          # Cohere embedding generation
│   │   ├── vector_store.py      # Qdrant storage operations
│   │   └── state_manager.py     # State persistence for resumability
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Structured logging setup
│   │   ├── retry.py             # Retry logic with exponential backoff
│   │   └── validators.py        # Input/output validation
│   └── cli/
│       ├── __init__.py
│       ├── crawl.py             # CLI: crawl command
│       ├── embed.py             # CLI: embed command
│       ├── upload.py            # CLI: upload command
│       └── pipeline.py          # CLI: full pipeline orchestration
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/
│   │   ├── test_crawler.py
│   │   ├── test_extractor.py
│   │   ├── test_chunker.py
│   │   ├── test_embedder.py
│   │   ├── test_vector_store.py
│   │   └── test_state_manager.py
│   ├── integration/
│   │   ├── test_full_pipeline.py
│   │   ├── test_cohere_integration.py
│   │   └── test_qdrant_integration.py
│   └── fixtures/
│       ├── sample_html/         # Sample HTML pages for testing
│       └── mock_responses/      # Mock API responses
├── data/                        # Runtime data directory (gitignored)
│   ├── state/                   # State checkpoints
│   ├── cache/                   # Optional: cached HTML/text
│   └── logs/                    # Log files
├── config/
│   ├── .env.example             # Example environment variables
│   └── config.yaml              # Optional: pipeline configuration
├── scripts/
│   ├── setup_qdrant.py          # Initialize Qdrant collection
│   └── validate_embeddings.py   # Validate vector search results
├── requirements.txt
├── requirements-dev.txt         # Development dependencies (pytest, etc.)
├── pyproject.toml               # Package metadata
└── README.md
```

**Structure Decision**: Single project structure (Option 1) with Python CLI tools and library architecture. The RAG pipeline is self-contained and separate from existing `frontend-book/` and deleted `backend-book/` directories. Modular design allows independent execution of crawl, embed, and upload stages with shared library code.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations**: This feature follows constitution principles without requiring complexity exceptions.
