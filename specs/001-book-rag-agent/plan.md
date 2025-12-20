# Implementation Plan: Floating RAG-Powered AI Agent for Book Content

**Branch**: `001-book-rag-agent` | **Date**: 2025-12-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-book-rag-agent/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a floating RAG-powered AI agent that integrates with the book UI to answer questions strictly from book content. Based on our research, the system will ingest book content from a sitemap, chunk text using semantic boundaries with 512-1024 token chunks and 20% overlap, create embeddings using Cohere's embed-multilingual-v3.0 model, and store in Qdrant Cloud. The backend will use FastAPI to provide APIs for ingestion and querying, while the frontend will feature a React-based floating chatbot UI integrated with the Docusaurus book interface. The agent will implement a strict retrieval-first approach to ensure zero hallucination, responding with "I don't know" when information isn't available in the book content.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Cohere Embed v3, Qdrant Cloud, OpenAI Agents SDK
**Storage**: Qdrant Cloud (vector database), with potential metadata in Neon Serverless Postgres
**Testing**: pytest
**Target Platform**: Linux server (backend API), Web (frontend integration with Docusaurus)
**Project Type**: Web application (backend API + frontend integration)
**Performance Goals**: <3 second response time for 95% of queries, handle 100 concurrent users
**Constraints**: Zero hallucination tolerance, retrieval-first approach, no external knowledge usage, free-tier compatible infrastructure
**Scale/Scope**: Single book with potential for multiple books, up to 1000+ pages per book, multiple concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Compliance Verification

**✅ Specification-First Authoring**: Feature originates from formal specs (Spec-Kit Plus) - [spec.md](spec.md) exists and follows template structure

**✅ Source-Grounded Accuracy**: AI agent will answer only from indexed book content with "I don't know" fallback when answer not found

**✅ Reproducibility**: All steps (content ingestion, indexing, chatbot behavior) will be fully reproducible from repository

**✅ Free-Tier Infrastructure Compatibility**: Using Qdrant Cloud (Free Tier) and Neon Serverless Postgres as specified in constitution

**✅ RAG Chatbot Stack**:
- Agent Framework: OpenAI Agents SDK (as specified in user requirements)
- Backend API: FastAPI (as specified in constitution)
- Vector Database: Qdrant Cloud (as specified in user requirements and constitution)
- Relational Database: Neon Serverless Postgres (as specified in constitution)

**✅ Chatbot Behavior Rules**:
- Answers derived only from indexed book content (requirement FR-002)
- Explicitly refuses questions outside book scope (requirement FR-005)
- Responses will be concise and citation-aware (requirement FR-010)

**✅ Constraints Verification**:
- RAG chatbot will not access external APIs for knowledge retrieval (requirement FR-002, FR-005)
- Free-tier compatible infrastructure only (Qdrant Free, Neon Serverless)
- Zero hallucination tolerance enforced through retrieval-first approach

### Post-Design Compliance Verification

**✅ Text Chunking Strategy**: Using semantic chunking with 512-1024 token chunks and 20% overlap preserves context while enabling precise retrieval, supporting source-grounded accuracy.

**✅ Embedding Model**: Cohere's embed-multilingual-v3.0 model supports the retrieval-first approach as required by the constitution.

**✅ API Contract**: OpenAPI specification ensures reproducible interfaces between frontend and backend components.

**✅ Data Model**: BookContent, Query, Response, and ChatSession entities support the core requirements without violating constitutional principles.

**✅ Frontend Integration**: Floating UI component integrated with Docusaurus maintains the book-focused experience as required.

## Project Structure

### Documentation (this feature)

```text
specs/001-book-rag-agent/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend-book/
├── src/
│   ├── models/
│   │   ├── query.py
│   │   ├── response.py
│   │   ├── book_content.py
│   │   └── chat_session.py
│   ├── services/
│   │   ├── ingestion_service.py
│   │   ├── embedding_service.py
│   │   ├── retrieval_service.py
│   │   ├── rag_agent_service.py
│   │   └── qdrant_service.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── ingest.py
│   │   │   ├── query.py
│   │   │   └── chat.py
│   │   └── middleware/
│   └── utils/
│       ├── text_chunker.py
│       └── sitemap_parser.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── requirements.txt
├── config/
│   └── settings.py
└── scripts/
    └── setup_qdrant.py

frontend-book/
├── src/
│   ├── components/
│   │   ├── FloatingRAGAgent.jsx
│   │   ├── ChatWindow.jsx
│   │   └── QueryInput.jsx
│   ├── services/
│   │   └── api.js
│   └── hooks/
│       └── useRAGAgent.js
├── docusaurus.config.ts
└── static/
    └── css/
        └── rag-agent.css
```

**Structure Decision**: Web application with separate backend and frontend components. The backend is a FastAPI application handling content ingestion, embedding, and RAG operations. The frontend is a Docusaurus site with React components for the floating RAG agent UI, integrated with the book interface.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations identified | All requirements comply with constitution |
