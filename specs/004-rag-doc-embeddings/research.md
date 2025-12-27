# Research: RAG Documentation Embeddings Pipeline

**Feature**: 004-rag-doc-embeddings
**Date**: 2025-12-26
**Purpose**: Resolve technical unknowns and document technology choices for RAG ingestion pipeline

---

## Research Questions

Based on Technical Context NEEDS CLARIFICATION items:

1. **Async/Concurrency**: asyncio vs threading for concurrent API calls
2. **Intermediate Storage**: Should we cache crawled HTML or extracted text?
3. **Cohere API**: Free tier rate limits
4. **Embedding Dimensions**: Cohere model output dimensions
5. **Text Chunking**: Best chunking library for semantic chunking
6. **Docusaurus Crawling**: Best practices for crawling Docusaurus sites

---

## 1. Async/Concurrency Strategy

### Decision: Use `asyncio` with `aiohttp` for I/O-bound operations

### Rationale:
- **I/O-bound workload**: Web crawling, API calls (Cohere, Qdrant) are primarily waiting on network responses
- **Python async ecosystem**: Well-supported with `aiohttp`, `asyncio`, and async-compatible clients
- **Cohere Python SDK**: Supports async operations via `cohere.AsyncClient`
- **Qdrant Python client**: Supports async operations via async mode
- **Concurrency control**: Easy to implement rate limiting with `asyncio.Semaphore`
- **Error handling**: Better control flow with async/await patterns

### Alternatives Considered:
- **Threading**: More complex state management, GIL limitations, harder to debug
- **Synchronous with batching**: Simpler but slower, doesn't leverage I/O wait time

### Implementation Notes:
```python
# Example structure
import asyncio
from cohere import AsyncClient as CohereClient
from qdrant_client import AsyncQdrantClient

async def process_batch(urls: list[str], semaphore: asyncio.Semaphore):
    async with semaphore:
        # Process with rate limiting
        pass
```

---

## 2. Intermediate Storage and Caching

### Decision: Cache extracted text files (not HTML) for debugging and resume capability

### Rationale:
- **Debugging value**: Extracted text allows inspection of cleaning quality without re-crawling
- **Resume capability**: If embedding fails, can restart from cached text without re-crawling
- **Storage efficiency**: Text is smaller than HTML (~30-50% reduction)
- **Pipeline decoupling**: Crawl stage can run independently; embed stage reads from cache

### Storage Schema:
```
data/
├── state/
│   ├── crawl_state.json      # URLs processed, timestamps
│   ├── embed_state.json       # Chunks embedded, last position
│   └── upload_state.json      # Vectors uploaded, batch IDs
├── cache/
│   └── extracted/
│       ├── {url_hash}.txt     # Extracted text
│       └── {url_hash}.meta.json  # Metadata (URL, title, timestamp)
└── logs/
    └── pipeline_{timestamp}.log
```

### Alternatives Considered:
- **No caching**: Simpler but requires re-crawling on any failure
- **Cache HTML**: Larger storage, doesn't help if extraction logic changes
- **SQLite database**: Overkill for simple key-value storage

---

## 3. Cohere API Rate Limits and Model Selection

### Decision: Use `embed-english-v3.0` model (1024 dimensions)

### Cohere Free Tier Limits (Trial API Key):
- **Rate limit**: 100 requests/minute (RPM)
- **Monthly quota**: 100 API calls total (VERY LIMITED - requires paid plan for production)
- **Batch size**: Up to 96 texts per embedding request
- **Max input tokens**: 512 tokens per text (after truncation)

### Production Plan Requirements:
- **Need paid plan**: Production plan ($0.0001/1k tokens) or higher
- **Rate limit (Production plan)**: 10,000 RPM
- **Expected cost**: For 3000 chunks @ 400 tokens avg = 1.2M tokens = ~$0.12

### Model Selection: `embed-english-v3.0`
- **Dimensions**: 1024 (good balance between quality and storage)
- **Performance**: State-of-art English embeddings
- **Input types**: Support for search_document and search_query types
- **Compatibility**: Works with Qdrant (supports 1024-dim vectors)

### Alternatives Considered:
- `embed-english-light-v3.0` (384 dims): Faster, smaller, but lower quality
- `embed-multilingual-v3.0` (1024 dims): Not needed (English-only docs)

### Implementation Strategy for Rate Limits:
```python
# Batch processing with rate limiting
BATCH_SIZE = 96  # Max per request
MAX_CONCURRENT = 5  # Stay under 100 RPM
DELAY_BETWEEN_BATCHES = 0.6  # 60s / 100 requests = 0.6s

async def embed_with_rate_limit(texts: list[str], semaphore: asyncio.Semaphore):
    async with semaphore:
        await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        return await cohere_client.embed(texts=texts, model="embed-english-v3.0")
```

---

## 4. Text Chunking Strategy

### Decision: Use `langchain-text-splitters` with `RecursiveCharacterTextSplitter`

### Rationale:
- **Semantic awareness**: Splits on sentence/paragraph boundaries when possible
- **Configurable overlap**: Maintains context between chunks
- **Token-aware**: Uses tiktoken for accurate token counting
- **Proven**: Battle-tested in production RAG systems
- **Lightweight**: No heavy ML dependencies

### Chunking Parameters:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,           # Target chunk size in tokens
    chunk_overlap=50,          # Overlap for context preservation
    length_function=tiktoken_len,  # Accurate token counting
    separators=["\n\n", "\n", ". ", " ", ""],  # Semantic boundaries
    keep_separator=True
)
```

### Chunking Tradeoffs:
| Parameter | Choice | Rationale |
|-----------|--------|-----------|
| Chunk size | 512 tokens | Balance between context and granularity; fits Cohere max |
| Overlap | 50 tokens (~10%) | Prevents context loss at boundaries |
| Separators | Paragraph → sentence → word | Maintains semantic units |

### Alternatives Considered:
- **Fixed-size splitting**: Simpler but breaks semantic units
- **Semantic chunking (LLM-based)**: Higher quality but expensive/slow
- **Custom implementation**: Unnecessary when proven solution exists

---

## 5. Docusaurus Crawling Best Practices

### Decision: Sitemap-first crawling with fallback to recursive crawling

### Rationale:
- **Docusaurus generates sitemaps**: `sitemap.xml` at root with all URLs
- **Efficient**: Get all URLs in one request instead of recursive crawling
- **Complete**: Sitemap includes all published pages
- **Respectful**: Fewer requests to server

### Crawling Strategy:
```python
1. Fetch sitemap.xml from https://ai-robitic-course-hackathon.vercel.app/sitemap.xml
2. Parse URLs from sitemap
3. Filter relevant URLs (docs/, blog/ paths)
4. Crawl each URL with async requests
5. Fallback: If sitemap fails, use recursive crawling from homepage
```

### HTML Content Extraction for Docusaurus:
```python
from bs4 import BeautifulSoup

def extract_docusaurus_content(html: str) -> dict:
    soup = BeautifulSoup(html, 'lxml')

    # Docusaurus content selectors
    main_content = soup.select_one('article') or soup.select_one('[role="main"]')
    title = soup.select_one('h1') or soup.select_one('title')

    # Remove navigation, footer, code line numbers
    for element in soup.select('nav, footer, .pagination-nav, .theme-code-block-highlighted-line'):
        element.decompose()

    return {
        'title': title.get_text(strip=True) if title else '',
        'content': main_content.get_text(separator='\n', strip=True) if main_content else '',
        'url': url
    }
```

### Alternatives Considered:
- **Recursive crawling only**: Slower, more requests, risk of missing pages
- **Headless browser (Playwright/Selenium)**: Overkill for static Docusaurus site
- **Manual URL list**: Not maintainable as docs evolve

---

## 6. Qdrant Collection Design

### Decision: Single collection with metadata filtering capabilities

### Collection Configuration:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client.create_collection(
    collection_name="docs-embeddings",
    vectors_config=VectorParams(
        size=1024,  # Cohere embed-english-v3.0
        distance=Distance.COSINE  # Standard for embeddings
    )
)

# Payload schema (metadata)
{
    "text": str,           # Original chunk text
    "url": str,            # Source page URL
    "title": str,          # Page title
    "chunk_index": int,    # Position in document
    "total_chunks": int,   # Total chunks for this document
    "token_count": int,    # Chunk size in tokens
    "crawled_at": str,     # ISO timestamp
    "doc_type": str,       # e.g., "tutorial", "reference", "blog"
}
```

### Indexing Strategy:
- **Vector index**: Automatic HNSW index by Qdrant (M=16, ef_construct=100)
- **Payload indexes**: Add indexes on frequently filtered fields
```python
client.create_payload_index(
    collection_name="docs-embeddings",
    field_name="url",
    field_schema=PayloadSchemaType.KEYWORD
)
```

### Alternatives Considered:
- **Multiple collections per doc type**: Unnecessary fragmentation
- **Separate collections for chunks vs full docs**: Adds complexity
- **Hierarchical structure**: Overkill for current scope

---

## 7. Error Handling and Retry Strategy

### Decision: Exponential backoff with jitter for all external API calls

### Implementation:
```python
import asyncio
import random
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_exponential_backoff(
    func: Callable[..., T],
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    *args,
    **kwargs
) -> T:
    """Retry with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # Add 10% jitter
            await asyncio.sleep(delay + jitter)

            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s: {e}")
```

### Retry Policies by Operation:
| Operation | Max Retries | Base Delay | Exceptions to Retry |
|-----------|-------------|------------|---------------------|
| HTTP crawl | 3 | 1s | Timeout, 5xx errors |
| Cohere API | 5 | 2s | Rate limit, 5xx errors |
| Qdrant upload | 5 | 1s | Connection errors, 5xx |

---

## 8. Testing Strategy

### Unit Tests:
- Mock external dependencies (HTTP, Cohere, Qdrant)
- Test each service module independently
- Validate chunking logic with known inputs
- Test state persistence and resume logic

### Integration Tests:
- Use Qdrant local instance or in-memory mode
- Mock Cohere with pre-computed embeddings
- Test full pipeline with sample Docusaurus HTML
- Verify end-to-end data flow

### Contract Tests:
- Validate Cohere API response format
- Validate Qdrant client compatibility
- Test error handling for API failures

---

## Summary of Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Concurrency** | asyncio + aiohttp | Efficient I/O-bound operations |
| **Caching** | Extracted text files | Debugging + resume capability |
| **Embeddings** | Cohere embed-english-v3.0 (1024d) | SOTA quality, Qdrant compatible |
| **Rate Limiting** | Semaphore + delays | Stay under 100 RPM limit |
| **Chunking** | langchain RecursiveCharacterTextSplitter | Semantic boundaries, token-aware |
| **Crawling** | Sitemap-first with fallback | Efficient, complete coverage |
| **Vector DB** | Qdrant Cloud (single collection) | Simple, scalable, free tier OK |
| **Retry Logic** | Exponential backoff with jitter | Robust error handling |
| **State Management** | JSON files | Simple, human-readable |
| **Testing** | pytest with mocks | Fast, reliable unit tests |

---

## Dependencies and Versions

```txt
# requirements.txt
aiohttp==3.9.1            # Async HTTP client
beautifulsoup4==4.12.2    # HTML parsing
lxml==4.9.3               # Fast XML/HTML parser
cohere==4.37              # Cohere SDK with async support
qdrant-client==1.7.0      # Qdrant async client
langchain-text-splitters==0.0.1  # Text chunking
tiktoken==0.5.2           # Token counting
pydantic==2.5.0           # Config validation
python-dotenv==1.0.0      # Environment variables
structlog==23.2.0         # Structured logging

# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
pytest-cov==4.1.0
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Cohere free tier exhaustion** | Document paid plan requirement; implement usage tracking |
| **Qdrant storage limits** | Monitor collection size; implement cleanup scripts |
| **Rate limit violations** | Implement conservative limits with buffer; add monitoring |
| **Incomplete crawling** | Validate against expected page count; log missing pages |
| **Memory issues with large sites** | Stream processing; batch operations; limit concurrent requests |
| **Network failures** | Retry logic; state checkpointing; resume capability |

---

## Next Steps (Phase 1: Design)

1. Generate `data-model.md` with entity definitions
2. Generate contracts (configuration schema, CLI interface)
3. Generate `quickstart.md` for developer onboarding
4. Update agent context with technology decisions
