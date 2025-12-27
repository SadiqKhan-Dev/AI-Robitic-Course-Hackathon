# CLI Interface Contract

**Feature**: 004-rag-doc-embeddings
**Date**: 2025-12-26
**Purpose**: Define command-line interface contracts for RAG pipeline scripts

---

## Overview

The RAG pipeline exposes four main CLI commands:
1. `crawl` - Crawl and extract documentation pages
2. `embed` - Generate embeddings from extracted text
3. `upload` - Upload embeddings to Qdrant
4. `pipeline` - Orchestrate full pipeline (crawl -> embed -> upload)

All commands follow consistent patterns:
- Exit code 0 on success, non-zero on failure
- JSON output mode for machine consumption
- Human-readable output by default
- Progress indicators for long-running operations
- Structured logging to log files

---

## 1. Crawl Command

### Purpose
Crawl Docusaurus site, extract content, cache extracted text and metadata.

### Usage

```bash
python -m rag_pipeline.cli.crawl [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--url` | `str` | From config | Docusaurus site URL |
| `--sitemap` | `str` | Auto-computed | Sitemap XML URL |
| `--output-dir` | `Path` | `./data/cache` | Cache directory |
| `--state-file` | `Path` | `./data/state/crawl_state.json` | State file path |
| `--max-pages` | `int` | `None` | Limit number of pages (for testing) |
| `--resume` | `flag` | `False` | Resume from state file |
| `--json` | `flag` | `False` | Output JSON format |
| `--verbose` / `-v` | `flag` | `False` | Verbose logging |

### Output (Human-readable)

```
🔍 Crawling Docusaurus site: https://ai-robitic-course-hackathon.vercel.app/
📄 Found 142 URLs in sitemap
⏳ Crawling pages... [==========>          ] 50/142 (35%)
✅ Completed: 142 pages
⚠️  Failed: 2 pages
📊 Summary:
   - Total URLs discovered: 142
   - Successfully crawled: 140
   - Failed: 2
   - Cached text files: 140
   - Duration: 3m 42s
```

### Output (JSON)

```json
{
  "status": "success",
  "stats": {
    "urls_discovered": 142,
    "urls_completed": 140,
    "urls_failed": 2,
    "duration_seconds": 222,
    "failed_urls": {
      "https://example.com/broken": "404 Not Found",
      "https://example.com/timeout": "Request timeout"
    }
  },
  "output_dir": "./data/cache/extracted",
  "state_file": "./data/state/crawl_state.json"
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (all or most pages crawled) |
| 1 | Configuration error |
| 2 | Network error (unable to reach site) |
| 3 | Partial failure (>20% pages failed) |
| 4 | State file error |

### Example Usage

```bash
# Basic crawl
python -m rag_pipeline.cli.crawl

# Resume from previous state
python -m rag_pipeline.cli.crawl --resume

# Limit pages for testing
python -m rag_pipeline.cli.crawl --max-pages 10

# JSON output
python -m rag_pipeline.cli.crawl --json | jq .
```

---

## 2. Embed Command

### Purpose
Generate embeddings from cached text files using Cohere API.

### Usage

```bash
python -m rag_pipeline.cli.embed [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input-dir` | `Path` | `./data/cache/extracted` | Cached text directory |
| `--output-file` | `Path` | `./data/embeddings.jsonl` | Output embeddings file |
| `--state-file` | `Path` | `./data/state/embed_state.json` | State file path |
| `--chunk-size` | `int` | `512` | Target chunk size (tokens) |
| `--chunk-overlap` | `int` | `50` | Overlap between chunks (tokens) |
| `--batch-size` | `int` | `96` | Cohere API batch size |
| `--max-rpm` | `int` | `100` | Max requests per minute |
| `--resume` | `flag` | `False` | Resume from state file |
| `--json` | `flag` | `False` | Output JSON format |
| `--verbose` / `-v` | `flag` | `False` | Verbose logging |

### Output (Human-readable)

```
📝 Chunking text from 140 documents...
✅ Created 2,847 chunks (avg 507 tokens/chunk)
🤖 Generating embeddings with Cohere (embed-english-v3.0)...
⏳ Embedding chunks... [===============>     ] 2100/2847 (74%)
   Rate: 95 requests/min | ETA: 2m 15s
✅ Embeddings generated: 2,847 chunks
💾 Saved to: ./data/embeddings.jsonl
📊 Summary:
   - Documents processed: 140
   - Total chunks: 2,847
   - Embeddings generated: 2,847
   - Failed: 0
   - API calls: 30 (batched)
   - Duration: 8m 32s
```

### Output (JSON)

```json
{
  "status": "success",
  "stats": {
    "documents_processed": 140,
    "total_chunks": 2847,
    "embeddings_generated": 2847,
    "embeddings_failed": 0,
    "api_calls": 30,
    "duration_seconds": 512,
    "avg_tokens_per_chunk": 507
  },
  "output_file": "./data/embeddings.jsonl",
  "state_file": "./data/state/embed_state.json"
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Configuration error |
| 2 | API error (auth, quota exceeded) |
| 3 | Partial failure (>10% chunks failed) |
| 4 | Input data error |

### Example Usage

```bash
# Basic embedding
python -m rag_pipeline.cli.embed

# Resume from previous state
python -m rag_pipeline.cli.embed --resume

# Custom chunk size
python -m rag_pipeline.cli.embed --chunk-size 400 --chunk-overlap 40

# JSON output
python -m rag_pipeline.cli.embed --json
```

---

## 3. Upload Command

### Purpose
Upload embeddings to Qdrant vector database.

### Usage

```bash
python -m rag_pipeline.cli.upload [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input-file` | `Path` | `./data/embeddings.jsonl` | Embeddings file |
| `--collection` | `str` | From config | Qdrant collection name |
| `--state-file` | `Path` | `./data/state/upload_state.json` | State file path |
| `--batch-size` | `int` | `100` | Upload batch size |
| `--recreate` | `flag` | `False` | Recreate collection (deletes existing) |
| `--resume` | `flag` | `False` | Resume from state file |
| `--json` | `flag` | `False` | Output JSON format |
| `--verbose` / `-v` | `flag` | `False` | Verbose logging |

### Output (Human-readable)

```
🗄️  Connecting to Qdrant: https://xyz.qdrant.tech
✅ Collection 'docs-embeddings' exists (14,230 vectors)
⏳ Uploading vectors... [==================>  ] 2500/2847 (88%)
   Rate: 98 vectors/min | ETA: 45s
✅ Upload complete: 2,847 vectors
🔍 Validating uploads...
✅ All vectors verified in collection
📊 Summary:
   - Total vectors uploaded: 2,847
   - Failed: 0
   - Collection size: 17,077 vectors
   - Duration: 1m 52s
```

### Output (JSON)

```json
{
  "status": "success",
  "stats": {
    "vectors_uploaded": 2847,
    "vectors_failed": 0,
    "collection_name": "docs-embeddings",
    "collection_size": 17077,
    "duration_seconds": 112
  },
  "qdrant_url": "https://xyz.qdrant.tech",
  "state_file": "./data/state/upload_state.json"
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Configuration error |
| 2 | Qdrant connection error |
| 3 | Partial failure (>5% vectors failed) |
| 4 | Input data error |

### Example Usage

```bash
# Basic upload
python -m rag_pipeline.cli.upload

# Recreate collection
python -m rag_pipeline.cli.upload --recreate

# Resume from previous state
python -m rag_pipeline.cli.upload --resume

# JSON output
python -m rag_pipeline.cli.upload --json
```

---

## 4. Pipeline Command

### Purpose
Orchestrate full pipeline: crawl -> embed -> upload.

### Usage

```bash
python -m rag_pipeline.cli.pipeline [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--skip-crawl` | `flag` | `False` | Skip crawling (use cache) |
| `--skip-embed` | `flag` | `False` | Skip embedding (use existing) |
| `--skip-upload` | `flag` | `False` | Skip upload |
| `--resume` | `flag` | `False` | Resume all stages from state |
| `--clean` | `flag` | `False` | Clean state/cache before starting |
| `--json` | `flag` | `False` | Output JSON format |
| `--verbose` / `-v` | `flag` | `False` | Verbose logging |

### Output (Human-readable)

```
🚀 Starting RAG Ingestion Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/3] 🔍 Crawl Phase
      ⏳ Crawling 142 pages...
      ✅ Completed in 3m 42s

[2/3] 🤖 Embed Phase
      ⏳ Generating embeddings for 2,847 chunks...
      ✅ Completed in 8m 32s

[3/3] 🗄️  Upload Phase
      ⏳ Uploading 2,847 vectors to Qdrant...
      ✅ Completed in 1m 52s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pipeline Complete
📊 Summary:
   - Pages crawled: 140
   - Chunks created: 2,847
   - Vectors uploaded: 2,847
   - Total duration: 14m 06s
```

### Output (JSON)

```json
{
  "status": "success",
  "phases": {
    "crawl": {
      "status": "success",
      "pages": 140,
      "duration_seconds": 222
    },
    "embed": {
      "status": "success",
      "chunks": 2847,
      "duration_seconds": 512
    },
    "upload": {
      "status": "success",
      "vectors": 2847,
      "duration_seconds": 112
    }
  },
  "total_duration_seconds": 846,
  "summary": {
    "pages_crawled": 140,
    "chunks_created": 2847,
    "vectors_uploaded": 2847
  }
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All phases succeeded |
| 1 | Configuration error |
| 2 | Crawl phase failed |
| 3 | Embed phase failed |
| 4 | Upload phase failed |
| 5 | Multiple phases failed |

### Example Usage

```bash
# Run full pipeline
python -m rag_pipeline.cli.pipeline

# Resume from interruption
python -m rag_pipeline.cli.pipeline --resume

# Skip crawling (use cached data)
python -m rag_pipeline.cli.pipeline --skip-crawl

# Clean start
python -m rag_pipeline.cli.pipeline --clean

# JSON output
python -m rag_pipeline.cli.pipeline --json
```

---

## Common Patterns

### Environment Variables

All commands respect environment variables:

```bash
# Required
export COHERE_API_KEY="your-cohere-key"
export QDRANT_URL="https://xyz.qdrant.tech"
export QDRANT_API_KEY="your-qdrant-key"

# Optional
export DOCUSAURUS_URL="https://ai-robitic-course-hackathon.vercel.app/"
export QDRANT_COLLECTION="docs-embeddings"
export CHUNK_SIZE=512
export CHUNK_OVERLAP=50
```

### Configuration File

Alternatively, use `.env` file:

```bash
# .env
COHERE_API_KEY=your-cohere-key
QDRANT_URL=https://xyz.qdrant.tech
QDRANT_API_KEY=your-qdrant-key
DOCUSAURUS_URL=https://ai-robitic-course-hackathon.vercel.app/
```

### Progress Indicators

All long-running commands show progress:
- Progress bar with percentage
- Current/total items
- Rate (items/min)
- ETA (estimated time remaining)

### Logging

Structured logs written to `./data/logs/`:
- Format: JSON lines
- Rotation: Daily
- Levels: DEBUG, INFO, WARNING, ERROR
- Fields: timestamp, level, message, context

### Error Handling

Consistent error reporting:
```json
{
  "status": "error",
  "error": {
    "type": "APIError",
    "message": "Cohere API rate limit exceeded",
    "details": {
      "retry_after": 60,
      "requests_remaining": 0
    }
  }
}
```

---

## Testing

### Unit Tests

Each command has unit tests:
- Mock external dependencies
- Test argument parsing
- Test error handling
- Test JSON output format

### Integration Tests

End-to-end pipeline tests:
- Use test Qdrant instance
- Mock Cohere with fixtures
- Test resume capability
- Test partial failures

### Example Test

```bash
# Test crawl with limited pages
pytest tests/unit/cli/test_crawl.py -v

# Test full pipeline (integration)
pytest tests/integration/test_full_pipeline.py -v
```

---

## Next Steps

- Define configuration schema contract
- Define API response contracts (Cohere, Qdrant)
- Generate quickstart.md with usage examples
