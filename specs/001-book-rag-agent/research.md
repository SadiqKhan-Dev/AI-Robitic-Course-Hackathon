# Research: Floating RAG-Powered AI Agent for Book Content

## Overview
This research document addresses the technical requirements and unknowns identified during the planning phase for implementing a floating RAG-powered AI agent that answers questions only from book content.

## Decision: Book Content Ingestion Strategy
**Rationale**: The system needs to ingest book content from the sitemap, chunk it, embed it, and store in Qdrant Cloud.
**Implementation**: Use a sitemap parser to extract all book URLs, fetch content from each page, process the HTML to extract text content, chunk the text into appropriate sizes, generate embeddings using Cohere Embed v3, and store in Qdrant Cloud.

**Alternatives considered**:
- PDF parsing: Would require additional processing and might not work well with Docusaurus-generated sites
- Direct database extraction: Not applicable since the book is likely served as static content
- Manual content entry: Would be too time-consuming and error-prone

## Decision: Text Chunking Strategy
**Rationale**: Text needs to be chunked appropriately for RAG retrieval to balance context preservation with retrieval precision.
**Implementation**: Use semantic chunking with 512-1024 token chunks, with 20% overlap to preserve context across chunks. This allows for sufficient context while enabling precise retrieval of relevant information.

**Alternatives considered**:
- Fixed-length chunks: Might break semantic boundaries and reduce retrieval quality
- Sentence-level chunks: Could be too granular for complex concepts
- Page-level chunks: Could be too large and dilute relevant information

## Decision: Embedding Model Selection
**Rationale**: The user specified Cohere Embed v3, which is appropriate for this use case.
**Implementation**: Use Cohere's embed-multilingual-v3.0 model which handles multiple languages and provides high-quality embeddings for semantic search.

**Alternatives considered**:
- OpenAI embeddings: Would work but not what the user specified
- Sentence transformers: Self-hosted option but requires more infrastructure
- Other Cohere models: v3 was specifically requested

## Decision: Vector Database Strategy
**Rationale**: The user specified Qdrant Cloud which offers managed vector database services.
**Implementation**: Use Qdrant Cloud with a collection for book content embeddings, implementing efficient similarity search for retrieval-augmented generation.

**Alternatives considered**:
- Pinecone: Alternative managed vector database but not what user specified
- Chroma: Open-source option but requires self-hosting
- Weaviate: Alternative vector database but Qdrant was specified

## Decision: RAG Agent Implementation
**Rationale**: The user specified using OpenAI Agents SDK (Gemini-compatible) for LLM orchestration.
**Implementation**: Create a custom agent that retrieves relevant chunks from Qdrant and generates responses based only on retrieved context, with fallback to "I don't know" when information is not available.

**Alternatives considered**:
- LangChain: Popular framework but OpenAI Agents SDK was specified
- Custom implementation: Possible but more complex than needed
- Other agent frameworks: Not specified by user

## Decision: Frontend Integration
**Rationale**: The floating chatbot UI needs to be visible on all book pages.
**Implementation**: Create a React component that can be integrated into the Docusaurus site, using a floating UI pattern that remains visible as users navigate through the book.

**Alternatives considered**:
- Standalone chat interface: Would require users to leave the book content
- Page-embedded chat: Would take up valuable screen real estate
- Modal interface: Would hide book content when active

## Decision: Zero Hallucination Strategy
**Rationale**: Critical requirement to prevent the AI from generating responses not grounded in book content.
**Implementation**: Implement a strict retrieval-first approach where the LLM only has access to retrieved context from the book. If no relevant content is retrieved, return "I don't know". Use content attribution to show sources.

**Alternatives considered**:
- Post-generation fact-checking: Would be complex and potentially unreliable
- Prompt engineering only: Not sufficient to guarantee zero hallucinations
- Multiple verification steps: Would slow down responses significantly