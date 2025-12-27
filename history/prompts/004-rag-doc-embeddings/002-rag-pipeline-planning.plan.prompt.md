---
id: 002
title: RAG Pipeline Planning
stage: plan
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-rag-doc-embeddings
branch: 004-rag-doc-embeddings
user: SadiqKhan-Dev
command: /sp.plan
labels: ["rag", "embeddings", "qdrant", "cohere", "docusaurus", "planning"]
links:
  spec: specs/004-rag-doc-embeddings/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-rag-doc-embeddings/plan.md
  - specs/004-rag-doc-embeddings/research.md
  - specs/004-rag-doc-embeddings/data-model.md
  - specs/004-rag-doc-embeddings/contracts/cli-interface.md
  - specs/004-rag-doc-embeddings/contracts/config-schema.yaml
  - specs/004-rag-doc-embeddings/quickstart.md
tests:
  - None (planning phase)
---

## Prompt

Plan the RAG ingestion pipeline for the deployed book website
Goal: Design a reliable pipeline that crawls published Docusaurus URLs, extracts and chunks text, generates embeddings, and stores them in Qdrant
Scope:
- URL discovery and crawling strategy
- Text extraction and cleaning
- Chunking approach with metadata schema
- Embedding generation using Cohere
- Qdrant collection design and insertion flow
Deliverables:
- Clear pipeline architecture
- Data flow diagram (logical steps)
- Decisions with tradeoffs (chunk size, metadata, batching)
- Risks and mitigation strategies
Constraints:
- Python-based implementation
- Qdrant Cloud free tier limitations
- Must support future retrieval and agent integration
Out of scope:
- Query/retrieval logic
- LLM agents or FastAPI integration
- Frontend concerns

## Response snapshot

Completed comprehensive planning for RAG ingestion pipeline with the following deliverables:

### Phase 0: Research (research.md)
- **Async/Concurrency**: Selected asyncio with aiohttp for I/O-bound operations
- **Caching**: Cache extracted text files (not HTML) for debugging and resume capability
- **Cohere API**: Use embed-english-v3.0 model (1024 dimensions), 100 RPM free tier limit
- **Chunking**: RecursiveCharacterTextSplitter from langchain with 512 tokens, 50 token overlap
- **Crawling**: Sitemap-first strategy with fallback to recursive crawling
- **Qdrant**: Single collection with metadata filtering, HNSW index, Cosine distance
- **Error Handling**: Exponential backoff with jitter for all external API calls

### Phase 1: Design Artifacts

**data-model.md**: Defined 5 core entities with Pydantic models:
- DocumentPage: Crawled page with extracted text and metadata
- TextChunk: Semantic text segments ready for embedding
- Embedding: Vector embeddings with model metadata
- VectorRecord: Qdrant-ready records with payloads
- State Management: CrawlState, EmbedState, UploadState for resumability

**contracts/cli-interface.md**: Defined 4 CLI commands:
- `crawl`: Discover and extract documentation pages
- `embed`: Generate embeddings from cached text
- `upload`: Upload vectors to Qdrant
- `pipeline`: Orchestrate full pipeline with resume capability

**contracts/config-schema.yaml**: Configuration schema with:
- Site, Cohere, Qdrant, chunking, crawling, storage settings
- Environment variable mapping
- Retry and concurrency configuration
- Validation and logging settings

**quickstart.md**: Developer onboarding guide with:
- 5-minute quick start
- Step-by-step installation and configuration
- Common workflows (development, production, incremental updates)
- Troubleshooting guide
- Testing instructions

### Technical Decisions

**Architecture**:
- Single Python project with modular library structure
- Three independent CLI stages (crawl, embed, upload) with orchestrator
- State checkpointing for resumability at each stage
- Async processing with rate limiting and retry logic

**Project Structure**:
```
rag-pipeline/
├── src/
│   ├── models/      # Pydantic data models
│   ├── services/    # Core business logic
│   ├── cli/         # CLI commands
│   └── utils/       # Shared utilities
├── tests/
│   ├── unit/        # Unit tests with mocks
│   └── integration/ # End-to-end tests
├── data/            # Runtime data (gitignored)
│   ├── cache/       # Extracted text
│   ├── state/       # Resume state
│   └── logs/        # Structured logs
└── scripts/         # Setup and validation
```

**Technology Stack**:
- Python 3.11+, asyncio, aiohttp
- beautifulsoup4 + lxml for HTML parsing
- Cohere embed-english-v3.0 (1024 dims)
- Qdrant Cloud free tier (1GB, 100 req/min)
- langchain-text-splitters for semantic chunking
- tiktoken for accurate token counting
- pydantic for config validation
- structlog for structured logging

**Key Metrics**:
- Target: 100-200 pages, 1000-3000 chunks
- Performance: <30 minutes for full pipeline
- Resume: <5% re-processing on interruption
- Search: <2s query latency, >0.7 similarity for relevant results

### Constitution Compliance
✅ PASS - Follows library-first, CLI interface, test-first, observability, and simplicity principles

## Outcome

- ✅ Impact: Comprehensive implementation plan ready for task generation
- 🧪 Tests: Testing strategy defined (unit, integration, contract tests)
- 📁 Files: 6 planning artifacts created (plan.md, research.md, data-model.md, 2 contracts, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable implementation tasks
- 🧠 Reflection: Resolved all NEEDS CLARIFICATION items through research phase; ready for implementation

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): PASS - All deliverables meet spec requirements
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Generate tasks with `/sp.tasks` command
