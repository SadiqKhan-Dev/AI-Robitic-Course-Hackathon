# Tasks: RAG Documentation Embeddings Pipeline

**Input**: Design documents from `/specs/004-rag-doc-embeddings/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md
**Tests**: No tests requested in spec.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md: `rag-pipeline/src/{models,services,utils,cli}`, `rag-pipeline/{tests,data,config,scripts}`, `rag-pipeline/tests/{unit,integration,fixtures}`
- [X] T002 Create `rag-pipeline/pyproject.toml` with Python 3.11+, name="rag-pipeline", version="0.1.0"
- [X] T003 [P] Create `rag-pipeline/requirements.txt` with: aiohttp==3.9.1, beautifulsoup4==4.12.2, lxml==4.9.3, cohere==4.37, qdrant-client==1.7.0, langchain-text-splitters==0.0.1, tiktoken==0.5.2, pydantic==2.5.0, python-dotenv==1.0.0, structlog==23.2.0
- [X] T004 [P] Create `rag-pipeline/requirements-dev.txt` with: pytest==7.4.3, pytest-asyncio==0.21.1, pytest-mock==3.12.0, pytest-cov==4.1.0
- [X] T005 [P] Create `rag-pipeline/config/.env.example` with: COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, DOCUSAURUS_URL, QDRANT_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP, LOG_LEVEL

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create `rag-pipeline/src/__init__.py` with package initialization
- [X] T007 [P] Create `rag-pipeline/src/config.py` with PipelineConfig class per data-model.md (pydantic BaseSettings, environment variables, validation)
- [X] T008 [P] Create `rag-pipeline/src/utils/logger.py` with structlog setup for structured logging (INFO level default, DEBUG optional)
- [X] T009 [P] Create `rag-pipeline/src/utils/__init__.py` and `rag-pipeline/src/utils/retry.py` with async retry_with_exponential_backoff function per research.md (max_retries=5, base_delay=1.0, max_delay=60.0, jitter)
- [X] T010 Create `rag-pipeline/src/utils/validators.py` with URL validation, input sanitization helpers

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Content Ingestion from Docusaurus (Priority: P1) 🎯 MVP

**Goal**: Crawl all public pages from deployed Docusaurus site, extract clean text content with metadata

**Independent Test**: Run `python -m src.cli.crawl --max-pages 5` and verify: (1) sitemap.xml is fetched, (2) pages are discovered and crawled, (3) text files with metadata are saved to `data/cache/extracted/`

### Implementation for User Story 1

- [X] T011 [US1] Create `rag-pipeline/src/models/__init__.py` and `rag-pipeline/src/models/document.py` with DocumentPage model per data-model.md (url, title, extracted_text, crawled_at, content_hash, metadata, validators)
- [X] T012 [P] [US1] Create `rag-pipeline/src/services/__init__.py` and `rag-pipeline/src/services/crawler.py` with DocusaurusCrawler class: (1) async fetch sitemap.xml, (2) parse URLs with lxml, (3) async crawl pages with aiohttp, (4) follow redirects, (5) rate limiting per research.md
- [X] T013 [US1] Create `rag-pipeline/src/services/extractor.py` with DocusaurusContentExtractor class: (1) parse HTML with BeautifulSoup + lxml, (2) select main content (`article` or `[role="main"]`), (3) remove nav/footer/code-block elements, (4) extract title from h1 or title tag, (5) clean and normalize text
- [X] T014 [US1] Create `rag-pipeline/src/services/state_manager.py` with CrawlState model per data-model.md: (1) track URLs discovered/completed/failed, (2) save/load JSON state for resume, (3) content_hash for change detection
- [X] T015 [P] [US1] Create `rag-pipeline/src/cli/__init__.py` and `rag-pipeline/src/cli/crawl.py` CLI module with: (1) argparse for --max-pages, --resume, --json, --verbose flags, (2) load config from config.py, (3) invoke crawler/extractor pipeline, (4) save extracted text + metadata to cache, (5) progress logging
- [X] T016 [US1] Create `rag-pipeline/data/` directory structure: `data/cache/extracted/`, `data/state/`, `data/logs/`
- [X] T017 [US1] Create `rag-pipeline/scripts/validate_crawl.py` validation script to verify: (1) all expected pages crawled, (2) extracted text meets min length (50 chars), (3) metadata files present

**Checkpoint**: User Story 1 complete - run validation: `python scripts/validate_crawl.py` and `python -m src.cli.crawl --max-pages 3`

---

## Phase 4: User Story 2 - Text Chunking and Embedding Generation (Priority: P2)

**Goal**: Split ingested documentation into semantic chunks and generate vector embeddings using Cohere API

**Independent Test**: Run `python -m src.cli.embed --max-pages 3` and verify: (1) text is split into chunks of ~512 tokens with overlap, (2) Cohere API returns 1024-dim vectors, (3) embeddings saved to `data/embeddings.jsonl`

### Implementation for User Story 2

- [X] T018 [US2] Create `rag-pipeline/src/models/chunk.py` with TextChunk model per data-model.md (chunk_id, text, source_url, source_title, chunk_index, total_chunks, token_count, char_start, char_end, metadata, validators)
- [X] T019 [US2] Create `rag-pipeline/src/models/embedding.py` with Embedding model per data-model.md (chunk_id, vector, model, created_at, chunk_ref, validator for 1024 dimensions)
- [X] T020 [US2] Create `rag-pipeline/src/services/chunker.py` with TextChunker class: (1) use langchain RecursiveCharacterTextSplitter per research.md, (2) chunk_size=512, chunk_overlap=50, (3) tiktoken for accurate token counting, (4) create TextChunk instances with metadata from DocumentPage
- [X] T021 [P] [US2] Create `rag-pipeline/src/services/embedder.py` with CohereEmbedder class: (1) initialize AsyncClient from cohere SDK, (2) batch texts (96 max per request), (3) rate limiting (100 RPM, 0.6s delay), (4) retry with exponential backoff, (5) generate 1024-dim embeddings with embed-english-v3.0 model
- [X] T022 [US2] Create `rag-pipeline/src/services/state_manager.py` extension with EmbedState model: (1) track chunks processed/failed, (2) batch progress, (3) save/load JSON state for resume
- [X] T023 [P] [US2] Create `rag-pipeline/src/cli/embed.py` CLI module with: (1) argparse for --chunk-size, --chunk-overlap, --resume, --json, --max-chunks flags, (2) load cached documents, (3) chunk documents, (4) generate embeddings, (5) save to embeddings.jsonl, (6) progress logging
- [X] T024 [US2] Create `rag-pipeline/data/embeddings.jsonl` output format per quickstart.md: `{"chunk_id": "...", "vector": [...], "metadata": {...}}`
- [X] T025 [US2] Create `rag-pipeline/scripts/validate_embed.py` validation script to verify: (1) all chunks have 1024-dim vectors, (2) metadata present, (3) no duplicate chunk_ids

**Checkpoint**: User Story 2 complete - run validation: `python scripts/validate_embed.py` and `python -m src.cli.embed --max-pages 3`

---

## Phase 5: User Story 3 - Vector Database Storage and Indexing (Priority: P3)

**Goal**: Upload generated embeddings to Qdrant Cloud and create searchable collection with proper indexing

**Independent Test**: Run `python -m src.cli.upload` and verify: (1) Qdrant collection created/exists, (2) all embeddings uploaded with payloads, (3) test search returns relevant results

### Implementation for User Story 3

- [X] T026 [US3] Create `rag-pipeline/src/models/embedding.py` extension with VectorRecord model: (1) id, vector, payload with required fields per data-model.md, (2) validator for payload fields, (3) to_qdrant_point() method for PointStruct conversion
- [X] T027 [P] [US3] Create `rag-pipeline/src/services/vector_store.py` with QdrantVectorStore class: (1) connect to Qdrant Cloud, (2) create collection with VectorParams (size=1024, distance=COSINE), (3) batch upsert with PointStruct, (4) payload index on url field, (5) retry with exponential backoff
- [X] T028 [US3] Create `rag-pipeline/src/services/state_manager.py` extension with UploadState model: (1) track vectors uploaded/failed, (2) batch progress, (3) save/load JSON state for resume
- [X] T029 [P] [US3] Create `rag-pipeline/src/cli/upload.py` CLI module with: (1) argparse for --recreate, --resume, --json, --batch-size flags, (2) load embeddings.jsonl, (3) convert to VectorRecords, (4) upload to Qdrant, (5) progress logging
- [X] T030 [US3] Create `rag-pipeline/scripts/setup_qdrant.py` setup script per quickstart.md: (1) validate Qdrant connection, (2) create collection if not exists, (3) display collection info (dimensions, distance, payload schema)
- [X] T031 [US3] Create `rag-pipeline/scripts/validate_embeddings.py` validation script per quickstart.md: (1) count vectors in collection, (2) run test search queries, (3) verify similarity scores > 0.7 for known topics

**Checkpoint**: User Story 3 complete - run validation: `python scripts/setup_qdrant.py` && `python -m src.cli.upload` && `python scripts/validate_embeddings.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that enable end-to-end pipeline execution

- [X] T032 [P] Create `rag-pipeline/src/cli/pipeline.py` orchestrator CLI: (1) run crawl → embed → upload sequentially, (2) --resume flag for partial execution, (3) --json for machine output, (4) progress bars and summary stats
- [X] T033 [P] Create `rag-pipeline/README.md` with: (1) Installation instructions, (2) Configuration guide, (3) CLI usage examples, (4) Troubleshooting section
- [X] T034 Add error handling throughout: (1) graceful failure with error codes, (2) meaningful error messages, (3) context logging for debugging
- [X] T035 [P] Add comprehensive logging: (1) structured logs with structlog, (2) progress indicators, (3) timing metrics per phase, (4) error context
- [X] T036 Create end-to-end test: (1) `python -m src.cli.pipeline --max-pages 3`, (2) verify all three phases complete, (3) validate final vector count

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (P1) → US2 (P2) → US3 (P3) sequentially (each builds on previous)
  - Can work on US2 and US3 in parallel once US1's output is available
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 output (extracted text in cache) - Must run after US1
- **User Story 3 (P3)**: Depends on US2 output (embeddings.jsonl) - Must run after US2

### Within Each User Story

- Models before services (entities first)
- Services before CLI (business logic before interface)
- State management early (for resume capability)
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T005)
- All Foundational tasks marked [P] can run in parallel (T007, T008, T009, T010)
- US1 tasks: T011, T012, T013 can run in parallel
- US2 tasks: T018, T020, T021, T023 can run in parallel
- US3 tasks: T026, T027, T028, T029, T030 can run in parallel
- Polish tasks T032 and T033 can run in parallel

---

## Parallel Execution Examples

### Setup Phase (Parallel)
```bash
Task T001: Create project directory structure
Task T002: Create pyproject.toml
Task T003: Create requirements.txt
Task T004: Create requirements-dev.txt
Task T005: Create config/.env.example
```

### Foundational Phase (Parallel)
```bash
Task T007: Create src/config.py
Task T008: Create src/utils/logger.py
Task T009: Create src/utils/retry.py
Task T010: Create src/utils/validators.py
```

### User Story 1 (Parallel within story)
```bash
Task T011: Create DocumentPage model
Task T012: Create crawler.py service
Task T013: Create extractor.py service
```

### User Story 2 (Parallel within story)
```bash
Task T018: Create TextChunk model
Task T020: Create chunker.py service
Task T021: Create embedder.py service
Task T023: Create embed CLI
```

### User Story 3 (Parallel within story)
```bash
Task T026: Create VectorRecord model
Task T027: Create vector_store.py service
Task T028: Extend state_manager.py
Task T029: Create upload CLI
Task T030: Create setup_qdrant.py script
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test with `python -m src.cli.crawl --max-pages 5`
5. Verify extracted text in `data/cache/extracted/`

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (extracts documentation text)
3. Add User Story 2 → Test independently → Demo (generates embeddings)
4. Add User Story 3 → Test independently → Demo (stores in Qdrant)
5. Polish → Final end-to-end pipeline demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (crawling + extraction)
   - Developer B: User Story 2 (chunking + embedding)
   - Developer C: User Story 3 (vector storage)
3. Stories complete and integrate sequentially (US1 output → US2 input → US2 output → US3 input)

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 36 |
| Setup Phase | 5 tasks |
| Foundational Phase | 5 tasks |
| User Story 1 (P1) | 7 tasks |
| User Story 2 (P2) | 8 tasks |
| User Story 3 (P3) | 6 tasks |
| Polish Phase | 5 tasks |
| Parallelizable Tasks | ~20 |

**MVP Scope**: User Story 1 only - after completing Phases 1-3, validate extraction works
