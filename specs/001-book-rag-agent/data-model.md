# Data Model: Floating RAG-Powered AI Agent for Book Content

## Overview
This document defines the data models for the RAG-powered AI agent that answers questions from book content.

## Core Entities

### BookContent
Represents a chunk of book content that has been processed and embedded for retrieval.

**Fields**:
- `id` (string): Unique identifier for the content chunk
- `url` (string): The source URL from which this content was extracted
- `title` (string): The title of the page/chapter this content belongs to
- `content` (string): The actual text content of the chunk
- `embedding` (list[float]): Vector embedding representation of the content
- `chunk_index` (int): Position of this chunk within the original document
- `metadata` (dict): Additional metadata (author, date, etc.)

**Validation**:
- `id` must be unique
- `content` must not be empty
- `embedding` must have the correct dimensionality for the chosen model

### Query
Represents a user's question or query to the RAG system.

**Fields**:
- `id` (string): Unique identifier for the query
- `user_id` (string): Identifier for the user making the query
- `question` (string): The natural language question from the user
- `timestamp` (datetime): When the query was made
- `page_context` (string, optional): URL of the current page when query was made

**Validation**:
- `question` must not be empty
- `user_id` should be present (anonymous users can have generated IDs)

### Response
Represents the AI agent's response to a user's query.

**Fields**:
- `id` (string): Unique identifier for the response
- `query_id` (string): Reference to the original query
- `answer` (string): The AI-generated answer based on book content
- `sources` (list[BookContent.id]): IDs of content chunks used to generate the answer
- `confidence` (float): Confidence score of the response (0.0-1.0)
- `timestamp` (datetime): When the response was generated
- `fallback_used` (bool): Whether the "I don't know" fallback was used

**Validation**:
- `answer` must not be empty (unless fallback_used is true)
- `confidence` must be between 0.0 and 1.0

### ChatSession
Represents a conversation session between a user and the AI agent.

**Fields**:
- `id` (string): Unique identifier for the session
- `user_id` (string): Identifier for the user
- `created_at` (datetime): When the session was started
- `last_interaction` (datetime): When the last message was exchanged
- `context` (list[dict]): Conversation history (messages exchanged)

**Validation**:
- `id` must be unique
- `context` should have reasonable size limits to prevent memory issues

## Relationships

```
[Query] --(1)-->[ChatSession]--(1)--> (Many)[Query]
[Response] --(1)-->[Query] (1-to-1 relationship)
[Query] --(Many)-->[BookContent] (Many-to-many via retrieval)
```

## State Transitions

### Query State Transitions
1. `created` → `processing`: When query is received and being processed
2. `processing` → `completed`: When response is generated successfully
3. `processing` → `failed`: When there's an error processing the query

### Response State Transitions
1. `generated` → `delivered`: When response is sent to the user
2. `delivered` → `rated`: When user provides feedback on the response

## Data Validation Rules

1. All user queries must be validated for appropriate content before processing
2. Retrieved book content chunks must be from the same book or related content only
3. Response attribution must accurately reference the source content chunks
4. Session data must be cleaned up after a period of inactivity
5. Embedding vectors must match the expected dimensionality for the model in use