<!-- SYNC IMPACT REPORT:
Version change: N/A (creating initial version) -> 1.0.0
Modified principles: N/A
Added sections: All principles and sections are newly added
Removed sections: N/A
Templates requiring updates: ⚠ pending review - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: RATIFICATION_DATE needs to be updated to actual date
-->
# Unified AI-Spec Driven Book with Integrated RAG Chatbot Constitution

## Core Principles

### Specification-First Authoring
All book content, structure, and behavior must originate from formal specs (Spec-Kit Plus).

### Source-Grounded Accuracy
All explanations must be derived from the authored book content; no hallucinated or external knowledge in the chatbot.

### Clarity for Technical Learners
Content must be understandable for beginner to intermediate developers with a computer science or web background.

### Reproducibility
Every step (authoring, deployment, indexing, chatbot behavior) must be fully reproducible from the repository.

### AI-Native Workflow Integrity
Claude Code must be used as the primary authoring agent, guided strictly by the constitution.

### Free-Tier Infrastructure Compatibility
Deployment must require no proprietary or paid services beyond free tiers (Qdrant Free, Neon Serverless).

## Key Standards

### Authoring Stack:
- Documentation: Docusaurus
- Specification System: Spec-Kit Plus
- AI Authoring Tool: Claude Code

### Publishing:
- Hosting: GitHub Pages
- Version control: GitHub (public repository)

### RAG Chatbot Stack:
- Agent Framework: OpenAI Agents / ChatKit SDKs
- Backend API: FastAPI
- Vector Database: Qdrant Cloud (Free Tier)
- Relational Database: Neon Serverless Postgres

### Chatbot Behavior Rules:
- Answers must be derived only from indexed book content
- Must support question-answering based on user-selected text only
- Must explicitly refuse questions outside the book's scope
- Responses must be concise, technical, and citation-aware

### Content Standards
- Writing level: Beginner to Intermediate
- Tone: Professional, instructional, and precise
- Structure:
  - Clear chapters and sections
  - Progressive difficulty
  - Practical examples and explanations
  - No filler content or speculative claims

## Development Workflow

### Constraints
- The book must be fully generated and structured via Spec-Kit Plus specs
- Claude Code must follow specs without improvising architecture
- RAG chatbot must not access external APIs for knowledge retrieval
- Free-tier compatible infrastructure only (Qdrant Free, Neon Serverless)
- Deployment must require no proprietary or paid services beyond free tiers

### Verification & Quality Controls
- All chatbot answers must be verifiable against stored embeddings
- Manual and automated checks to ensure no hallucinated responses
- Book build must succeed via a clean repository clone and install
- Clear README with setup, deployment, and usage instructions

### Deliverables
- Docusaurus Book Repository
  - Spec-Kit Plus specifications
  - AI-generated content via Claude Code
  - Clean, structured documentation
- Published Documentation Site
  - Deployed on GitHub Pages
  - Publicly accessible
- Integrated RAG Chatbot
  - Embedded UI within the documentation site
  - FastAPI backend with vector search
  - Qdrant-indexed book content
  - Neon-backed metadata and session storage

### Technical Documentation
- Architecture overview
- RAG data flow explanation
- Setup and deployment guide

### Success Criteria
- Book is fully spec-driven and AI-authored
- GitHub Pages site builds and deploys successfully
- RAG chatbot answers accurately using only book content
- Selected-text question answering works reliably
- No hallucinated or out-of-scope responses
- Repository can be cloned, built, and deployed without errors

### Non-Goals
- No general-purpose chatbot behavior
- No reliance on external knowledge bases
- No manual content writing outside Claude Code execution

## Governance

Constitution is binding and must be followed strictly when generating, modifying, or extending any part of the project. All decisions and implementations must align with the specified principles, standards, and requirements. Includes versioning policy and compliance review expectations.

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-12-17