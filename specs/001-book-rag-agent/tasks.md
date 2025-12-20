# Implementation Tasks: Floating RAG-Powered AI Agent for Book Content

**Feature**: Floating RAG-Powered AI Agent for Book Content  
**Branch**: `001-book-rag-agent`  
**Created**: 2025-12-20  
**Status**: Draft  

## Implementation Strategy

This document outlines the implementation tasks for the floating RAG-powered AI agent that answers questions from book content. The approach follows an MVP-first strategy, with User Story 1 as the initial deliverable, followed by enhancements in subsequent user stories.

The implementation is organized into phases:
1. Setup: Project initialization and environment configuration
2. Foundational: Core infrastructure and shared components
3. User Stories: Implementation of prioritized user stories (P1, P2, P3)
4. Polish: Cross-cutting concerns and final touches

## Dependencies

User stories are designed to be as independent as possible, with foundational components implemented first. User Story 1 (P1) must be completed before User Story 2 (P2) and User Story 3 (P3), as they build upon the core functionality.

## Parallel Execution Examples

- Backend API development can proceed in parallel with frontend UI development
- Ingestion service development can run alongside query/retrieval service development
- Unit tests can be written in parallel with implementation components

---

## Phase 1: Setup

### Goal
Initialize project structure and configure development environment with necessary dependencies.

### Independent Test Criteria
- Project structure matches implementation plan
- Dependencies are properly configured
- Basic API server can start without errors
- Frontend can build and run without errors

### Tasks

- [X] T001 Create backend-book directory structure per implementation plan
- [X] T002 Create frontend-book directory structure per implementation plan
- [X] T003 [P] Set up backend requirements.txt with FastAPI, Cohere, Qdrant, OpenAI dependencies
- [X] T004 [P] Set up frontend package.json with Docusaurus dependencies
- [X] T005 Create .env.example file with required environment variables
- [X] T006 Set up gitignore files for both backend and frontend

---

## Phase 2: Foundational Components

### Goal
Implement core infrastructure and shared components required by all user stories.

### Independent Test Criteria
- Qdrant collection is created and accessible
- Embedding service can generate vector representations
- Text chunking service can split content appropriately
- Sitemap parser can extract URLs from book sitemap

### Tasks

- [X] T007 Set up Qdrant service in src/services/qdrant_service.py
- [X] T008 Create embedding service in src/services/embedding_service.py using Cohere
- [X] T009 Create text chunker utility in src/utils/text_chunker.py with semantic chunking
- [X] T010 Create sitemap parser utility in src/utils/sitemap_parser.py
- [X] T011 [P] Create BookContent model in src/models/book_content.py
- [X] T012 [P] Create Query model in src/models/query.py
- [X] T013 [P] Create Response model in src/models/response.py
- [X] T014 [P] Create ChatSession model in src/models/chat_session.py
- [X] T015 Create configuration settings in config/settings.py
- [X] T016 Create setup script for Qdrant collection in scripts/setup_qdrant.py

---

## Phase 3: User Story 1 - Ask Questions from Book Content (Priority: P1)

### Goal
As a reader browsing through the book, I want to be able to ask questions about the book content and receive accurate answers directly from the book material. The AI agent should appear as a floating chat interface that is accessible from any page in the book.

### Independent Test Criteria
- Can ask various questions about book content and receive accurate answers grounded in book text
- When question cannot be answered from book content, system responds with "I don't know"
- When asking questions related to current page content, system provides answers with context from the current page

### Acceptance Tests
- Given user is viewing any page in the book, when user opens the floating chatbot and asks a question about the book content, then the AI agent responds with an accurate answer grounded in the book text
- Given user asks a question that cannot be answered from the book content, when the AI agent processes the query, then it responds with "I don't know" or similar fallback message
- Given user asks a question related to the current page content, when user submits the query, then the AI provides answers with context from the current page

### Tasks

- [X] T017 Create ingestion service in src/services/ingestion_service.py
- [X] T018 Create retrieval service in src/services/retrieval_service.py
- [X] T019 Create RAG agent service in src/services/rag_agent_service.py
- [X] T020 [P] [US1] Create ingest API route in src/api/routes/ingest.py
- [X] T021 [P] [US1] Create query API route in src/api/routes/query.py
- [X] T022 [P] [US1] Create chat API route in src/api/routes/chat.py
- [X] T023 [P] [US1] Create main API application in src/api/main.py
- [X] T024 [P] [US1] Create FloatingRAGAgent component in frontend-book/src/components/FloatingRAGAgent.jsx
- [X] T025 [P] [US1] Create ChatWindow component in frontend-book/src/components/ChatWindow.jsx
- [X] T026 [P] [US1] Create QueryInput component in frontend-book/src/components/QueryInput.jsx
- [X] T027 [P] [US1] Create API service in frontend-book/src/services/api.js
- [X] T028 [P] [US1] Create useRAGAgent hook in frontend-book/src/hooks/useRAGAgent.js
- [X] T029 [P] [US1] Integrate floating agent into Docusaurus config in docusaurus.config.ts
- [X] T030 [P] [US1] Add CSS styling for floating agent in frontend-book/static/css/rag-agent.css
- [X] T031 [US1] Implement basic query endpoint with retrieval and response generation
- [X] T032 [US1] Implement fallback response ("I don't know") when content not found
- [X] T033 [US1] Implement page context awareness in query processing
- [X] T034 [US1] Test end-to-end functionality with sample book content

---

## Phase 4: User Story 2 - Global Book Queries (Priority: P2)

### Goal
As a reader, I want to ask questions that might span multiple sections of the book, so the AI agent should be able to search across the entire book content to provide comprehensive answers.

### Independent Test Criteria
- Can ask questions that require information from multiple book sections
- AI retrieves and synthesizes information from across the book
- Answers are comprehensive and draw from relevant sections throughout the book

### Acceptance Tests
- Given user wants information that spans multiple chapters, when user asks a cross-chapter question, then the AI agent provides a comprehensive answer drawing from relevant sections throughout the book

### Tasks

- [X] T035 [US2] Enhance retrieval service to support global book queries
- [X] T036 [US2] Update query endpoint to support global search mode
- [X] T037 [US2] Implement cross-section synthesis in RAG agent service
- [X] T038 [US2] Update frontend to indicate global search mode
- [X] T039 [US2] Test global query functionality with multi-section questions

---

## Phase 5: User Story 3 - Page-Level Context Queries (Priority: P3)

### Goal
As a reader, I want the AI agent to understand the context of the current page I'm viewing, so it can provide more targeted and relevant answers to my questions.

### Independent Test Criteria
- When asking questions on specific pages, AI leverages the current page context when formulating responses
- Responses prioritize information from the current page when relevant
- Context-aware responses are more targeted and relevant

### Acceptance Tests
- Given user is viewing a specific page with particular content, when user asks a question related to that content, then the AI agent prioritizes information from the current page in its response

### Tasks

- [X] T040 [US3] Enhance query endpoint to accept and utilize page context
- [X] T041 [US3] Update RAG agent service to prioritize current page context
- [X] T042 [US3] Update frontend to pass page URL context with queries
- [X] T043 [US3] Test page-level context functionality with page-specific questions

---

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Address cross-cutting concerns, optimize performance, and add finishing touches to the implementation.

### Independent Test Criteria
- System handles edge cases appropriately
- Performance requirements are met
- Error handling is robust
- System is production-ready

### Tasks

- [X] T044 Implement handling for extremely long or complex queries
- [X] T045 Add proper error handling for vector database unavailability
- [X] T046 Implement query rate limiting and user session management
- [X] T047 Add logging and monitoring for production use
- [X] T048 Optimize response time to meet <3 second requirement
- [X] T049 Implement caching for frequently asked questions
- [X] T050 Add comprehensive error messages for debugging
- [X] T051 Write integration tests for all API endpoints
- [X] T052 Perform load testing to ensure 100 concurrent users support
- [X] T053 Document API endpoints with examples
- [X] T054 Add user feedback mechanism for response quality
- [X] T055 Finalize UI/UX with responsive design and accessibility