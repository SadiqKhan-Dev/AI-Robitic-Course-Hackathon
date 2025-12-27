# RAG Pipeline - AI Robotics Book Assistant

A free RAG (Retrieval-Augmented Generation) system for the AI Robotics Book using:
- **Qdrant** - Free cloud vector database (16 documents embedded)
- **Sentence Transformers** - Free embeddings (all-MiniLM-L6-v2)
- **Google Gemini** - Free LLM tier (gemini-1.5-flash)

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   User      │────▶│  Streamlit UI    │────▶│  RAG Agent  │
│  Interface  │     │  / CLI / API     │     │  (LangChain)│
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                    │
                      ┌─────────────────────────────┼─────────────────────────────┐
                      │                             │                             │
                      ▼                             ▼                             ▼
            ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
            │ Qdrant Vector   │         │ Sentence Trans- │         │ Google Gemini  │
            │ Database        │◀────────│ formers Embed   │────────▶│ LLM             │
            │ (16 documents)  │         │ (all-MiniLM)    │         │ (Flash Model)   │
            └─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
cd rag-pipeline
pip install -r requirements.txt
```

### 2. Configure Gemini API Key

Edit `config.yaml` and set your Gemini API key:

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY_HERE"
```

Get your free API key from: https://aistudio.google.com/app/apikey

### 3. Run the Application

**Streamlit UI (Recommended):**
```bash
python main.py ui
# OR
streamlit run src/ui/app.py
```

**CLI Mode:**
```bash
python main.py cli
```

**Check Status:**
```bash
python main.py status
```

## Usage

1. Open the Streamlit UI at `http://localhost:8501`
2. Type questions about the AI Robotics Book
3. The agent will:
   - Search the knowledge base
   - Retrieve relevant documents
   - Generate accurate answers with citations

## Sample Questions

- "What is the Vision Language Action (VLA) pipeline?"
- "How does speech recognition work in the robot?"
- "Explain the capstone autonomous humanoid project"
- "What are the performance considerations for real-time control?"

## Project Structure

```
rag-pipeline/
├── config.yaml              # Central configuration
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md               # This file
└── src/
    ├── agents/
    │   └── rag_agent.py    # RAG Agent implementation
    ├── services/
    │   ├── qdrant_service.py      # Vector database service
    │   └── embedding_service.py   # Embeddings + Gemini LLM
    └── ui/
        └── app.py          # Streamlit UI
```

## Free Tier Limits

| Service | Free Limit | RAG Pipeline Usage |
|---------|------------|-------------------|
| Qdrant Cloud | 1GB storage | ~16 docs (minimal) |
| Gemini 1.5 Flash | 15 RPM, 1M tokens/day | Well within limits |
| Sentence Transformers | Unlimited (local) | No API calls |

## Troubleshooting

**Qdrant Connection Timeout:**
- Check your internet connection
- The Qdrant cloud cluster may be waking up (wait 30s and retry)

**Gemini API Error:**
- Verify API key in config.yaml
- Check quota at https://aistudio.google.com

**Embedding Dimension Mismatch:**
- Ensure vector_size in config.yaml matches model (384 for all-MiniLM-L6-v2)
