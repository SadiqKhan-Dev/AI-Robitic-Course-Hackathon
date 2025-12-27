# Quickstart: RAG Documentation Embeddings Pipeline

**Feature**: 004-rag-doc-embeddings
**Date**: 2025-12-26
**Purpose**: Get started quickly with the RAG ingestion pipeline

---

## Prerequisites

- **Python 3.11+** installed
- **Cohere API key** (sign up at https://cohere.com)
- **Qdrant Cloud instance** (free tier at https://qdrant.tech)
- **Git** for cloning the repository

---

## Quick Start (5 minutes)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd AI-Robitic-Course-Hackathon/rag-pipeline
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file in `rag-pipeline/` directory:

```bash
# .env
COHERE_API_KEY=your-cohere-api-key-here
QDRANT_URL=https://xyz-abc.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key-here
```

### 4. Initialize Qdrant Collection

```bash
python scripts/setup_qdrant.py
```

**Expected output:**
```
✅ Connected to Qdrant: https://xyz-abc.qdrant.tech
✅ Collection 'docs-embeddings' created (1024 dimensions, Cosine distance)
```

### 5. Run Full Pipeline

```bash
python -m src.cli.pipeline
```

**Expected output:**
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
```

### 6. Validate Results

```bash
python scripts/validate_embeddings.py
```

**Expected output:**
```
🔍 Testing search functionality...
✅ Query 1: "What is ROS 2?" → 5 results (similarity > 0.8)
✅ Query 2: "NVIDIA Isaac" → 5 results (similarity > 0.75)
✅ Query 3: "Vision Language Action" → 5 results (similarity > 0.82)
✅ All validation tests passed!
```

---

## Step-by-Step Guide

### Detailed Installation

#### 1. System Dependencies

**Windows:**
```powershell
# Install Python 3.11 from python.org
# Verify installation
python --version  # Should show 3.11+
```

**Linux/Mac:**
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv  # Ubuntu/Debian
brew install python@3.11  # macOS

# Verify
python3.11 --version
```

#### 2. Virtual Environment Setup

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (for testing)
pip install -r requirements-dev.txt
```

**Dependencies installed:**
- `aiohttp` - Async HTTP client
- `beautifulsoup4`, `lxml` - HTML parsing
- `cohere` - Cohere API client
- `qdrant-client` - Qdrant vector database
- `langchain-text-splitters` - Text chunking
- `tiktoken` - Token counting
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `structlog` - Structured logging

### Detailed Configuration

#### 1. Get API Keys

**Cohere:**
1. Sign up at https://cohere.com
2. Navigate to Dashboard → API Keys
3. Create new API key (Trial or Production)
4. Copy the key

**Qdrant:**
1. Sign up at https://qdrant.tech
2. Create new cluster (Free tier: 1GB)
3. Copy cluster URL and API key from cluster details

#### 2. Create Configuration Files

**Option A: .env file (Recommended)**

```bash
# rag-pipeline/.env
COHERE_API_KEY=your-cohere-key-here
QDRANT_URL=https://xyz-abc-def.qdrant.tech
QDRANT_API_KEY=your-qdrant-key-here

# Optional overrides
DOCUSAURUS_URL=https://ai-robitic-course-hackathon.vercel.app/
QDRANT_COLLECTION=docs-embeddings
CHUNK_SIZE=512
CHUNK_OVERLAP=50
LOG_LEVEL=INFO
```

**Option B: config.yaml**

```yaml
# rag-pipeline/config/config.yaml
pipeline:
  site:
    url: "https://ai-robitic-course-hackathon.vercel.app/"
  cohere:
    api_key: "your-key-here"  # Better: use env var
    model: "embed-english-v3.0"
  qdrant:
    url: "https://xyz.qdrant.tech"
    api_key: "your-key-here"  # Better: use env var
    collection_name: "docs-embeddings"
```

#### 3. Verify Configuration

```bash
python -c "
from src.config import PipelineConfig
config = PipelineConfig()
print(f'✅ Config loaded: {config.qdrant_collection}')
"
```

### Running Individual Stages

#### Stage 1: Crawl

```bash
# Basic crawl
python -m src.cli.crawl

# Test with limited pages
python -m src.cli.crawl --max-pages 10

# Resume from interruption
python -m src.cli.crawl --resume

# JSON output
python -m src.cli.crawl --json | jq .
```

**Output location:** `./data/cache/extracted/`
- `{url_hash}.txt` - Extracted text
- `{url_hash}.meta.json` - Metadata

#### Stage 2: Embed

```bash
# Generate embeddings from cache
python -m src.cli.embed

# Custom chunk size
python -m src.cli.embed --chunk-size 400 --chunk-overlap 40

# Resume from interruption
python -m src.cli.embed --resume
```

**Output location:** `./data/embeddings.jsonl`

**Format:**
```json
{"chunk_id": "abc123_0", "vector": [0.123, ...], "metadata": {...}}
{"chunk_id": "abc123_1", "vector": [0.456, ...], "metadata": {...}}
```

#### Stage 3: Upload

```bash
# Upload to Qdrant
python -m src.cli.upload

# Recreate collection (deletes existing)
python -m src.cli.upload --recreate

# Resume from interruption
python -m src.cli.upload --resume
```

**Qdrant collection:** `docs-embeddings`

---

## Common Workflows

### Development Workflow

```bash
# 1. Test crawl with limited pages
python -m src.cli.crawl --max-pages 5 --verbose

# 2. Check extracted text
ls -lh data/cache/extracted/
cat data/cache/extracted/*.txt | head -50

# 3. Test embedding with cached data
python -m src.cli.embed --verbose

# 4. Validate embeddings file
head -1 data/embeddings.jsonl | jq .

# 5. Upload to Qdrant
python -m src.cli.upload --verbose
```

### Production Workflow

```bash
# 1. Clean previous state
rm -rf data/state/*.json

# 2. Run full pipeline
python -m src.cli.pipeline --json > pipeline_log.json

# 3. Check results
jq '.summary' pipeline_log.json

# 4. Validate search
python scripts/validate_embeddings.py
```

### Incremental Update Workflow

```bash
# 1. Crawl (skips unchanged pages via content_hash)
python -m src.cli.crawl --resume

# 2. Embed only new chunks
python -m src.cli.embed --resume

# 3. Upload only new vectors
python -m src.cli.upload --resume
```

---

## Troubleshooting

### Issue: Cohere Rate Limit Exceeded

**Error:**
```
❌ APIError: Rate limit exceeded (100 requests/min)
```

**Solution:**
```bash
# Reduce max RPM in config
export MAX_RPM=80
python -m src.cli.embed --max-rpm 80
```

### Issue: Qdrant Connection Failed

**Error:**
```
❌ Cannot connect to Qdrant: Connection refused
```

**Solution:**
1. Verify Qdrant URL in `.env`
2. Check API key is correct
3. Test connection:
```bash
curl -H "api-key: YOUR_KEY" https://xyz.qdrant.tech/collections
```

### Issue: Out of Memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```bash
# Reduce concurrent requests
python -m src.cli.crawl --max-concurrent 3

# Reduce batch size
python -m src.cli.embed --batch-size 50
```

### Issue: Resume Not Working

**Error:**
```
⚠️  State file not found, starting fresh
```

**Solution:**
```bash
# Check state files exist
ls -l data/state/

# If missing, pipeline will start fresh
# To resume, ensure state files are preserved
```

### Issue: Test Queries Return No Results

**Error:**
```
⚠️  Query "ROS 2" returned 0 results
```

**Solution:**
1. Verify vectors were uploaded:
```bash
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='...', api_key='...')
print(client.count('docs-embeddings'))
"
```

2. Check collection exists and has vectors
3. Try lowering similarity threshold in validation script

---

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific module tests
pytest tests/unit/test_crawler.py -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Integration Tests

```bash
# Run integration tests (requires test Qdrant instance)
pytest tests/integration/ -v

# Run full pipeline test
pytest tests/integration/test_full_pipeline.py -v
```

### Manual Validation

```bash
# Test crawl
python -m src.cli.crawl --max-pages 3 --json | jq '.stats'

# Test embed
python -m src.cli.embed --json | jq '.stats'

# Test upload
python -m src.cli.upload --json | jq '.stats'

# Test search
python scripts/validate_embeddings.py
```

---

## Directory Structure After Setup

```
rag-pipeline/
├── data/
│   ├── cache/
│   │   └── extracted/
│   │       ├── a1b2c3.txt
│   │       ├── a1b2c3.meta.json
│   │       └── ...
│   ├── state/
│   │   ├── crawl_state.json
│   │   ├── embed_state.json
│   │   └── upload_state.json
│   ├── logs/
│   │   └── pipeline_2025-12-26.log
│   └── embeddings.jsonl
├── src/
│   ├── models/
│   ├── services/
│   ├── cli/
│   └── utils/
├── tests/
├── config/
│   └── .env
├── scripts/
│   ├── setup_qdrant.py
│   └── validate_embeddings.py
├── requirements.txt
└── README.md
```

---

## Next Steps

1. **Implement retrieval logic** - Query the vector database
2. **Integrate with LLM agent** - Use retrieved chunks for RAG
3. **Build FastAPI service** - Expose search API
4. **Add frontend** - User interface for search

---

## Resources

- **Cohere Docs**: https://docs.cohere.com/docs/embeddings
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Docusaurus**: https://docusaurus.io/
- **Feature Spec**: [spec.md](./spec.md)
- **Data Model**: [data-model.md](./data-model.md)
- **CLI Contract**: [contracts/cli-interface.md](./contracts/cli-interface.md)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in `data/logs/`
3. Run with `--verbose` flag for detailed output
4. Open issue in project repository
