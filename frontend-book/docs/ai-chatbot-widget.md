---
sidebar_position: 99
---

# AI Chatbot Widget

Add an intelligent popup chatbot to your documentation site that answers questions about the AI Robotics Book.

## Quick Install

Add this to your `docusaurus.config.ts` or any HTML page:

```html
<!-- Add to <head> -->
<link rel="stylesheet" href="/js/ai-chatbot-widget.css">

<!-- Add before </body> -->
<script src="/js/ai-chatbot-widget.js"></script>
```

## With Custom Options

```html
<script>
  window.AI_CHAT_API_URL = 'http://localhost:8000';
  window.AI_CHAT_PROVIDER = 'qdrant';
  window.AI_CHAT_COLOR = '#6366f1';
  window.AI_CHAT_TITLE = 'AI Book Assistant';
</script>
<script src="/js/ai-chatbot-widget.js"></script>
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `AI_CHAT_API_URL` | Backend API URL | `/api/chat` |
| `AI_CHAT_PROVIDER` | Embedding provider | `qdrant` |
| `AI_CHAT_COLOR` | Primary brand color | `#6366f1` |
| `AI_CHAT_TITLE` | Header title | `AI Book Assistant` |
| `AI_CHAT_POSITION` | `bottom-right` or `bottom-left` | `bottom-right` |

## Supported Providers

### Qdrant + SentenceTransformers (Recommended - Free)

Uses local embeddings - no API keys needed:

```html
<script>
  window.AI_CHAT_PROVIDER = 'qdrant';
</script>
<script src="/js/ai-chatbot-widget.js"></script>
```

### Cohere + Qdrant

Higher quality embeddings (requires API key):

```html
<script>
  window.AI_CHAT_API_URL = 'https://your-api.com/chat';
  window.AI_CHAT_PROVIDER = 'cohere';
</script>
<script src="https://your-api.com/js/ai-chatbot-widget.js"></script>
```

Get API key: [cohere.com](https://cohere.com/)

### HuggingFace + Qdrant

Open source embeddings:

```html
<script>
  window.AI_CHAT_API_URL = 'https://your-api.com/chat';
  window.AI_CHAT_PROVIDER = 'huggingface';
</script>
```

Get token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## API Endpoints

Your backend should implement:

### POST /api/chat

```json
{
  "message": "What is VLA pipeline?",
  "provider": "qdrant"
}
```

Response:

```json
{
  "success": true,
  "answer": "VLA stands for Vision-Language-Action...",
  "sources": [
    {
      "title": "Voice to Action Pipelines",
      "url": "/docs/ai-robotics/vla-pipelines",
      "score": 0.85
    }
  ]
}
```

## Features

- **Smart Answers**: Uses RAG to answer from book content
- **Source Citations**: Shows which docs were used
- **Multi-Provider**: Supports Qdrant, Cohere, HuggingFace
- **Responsive**: Works on mobile and desktop
- **Customizable**: Colors, position, title
- **Keyboard Support**: Press Enter to send

## Screenshot

```
┌─────────────────────────────────┐
│ 🤖 AI Book Assistant      [X]  │
│ [Qdrant Vector DB]              │
├─────────────────────────────────┤
│ 👋 Welcome! Ask me about the    │
│    AI Robotics Book...          │
│                                 │
│    [VLA Pipeline] [Autonomous]  │
│    [LLM Planning]               │
├─────────────────────────────────┤
│ [ Type a question...      ] [➤] │
└─────────────────────────────────┘
```

## Server Setup

Run the FastAPI backend:

```bash
cd rag-pipeline
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Then add the widget to your site!

## Troubleshooting

**Widget not showing?**
- Check browser console for errors
- Verify API URL is accessible

**API errors?**
- Ensure backend is running
- Check CORS settings

**No sources found?**
- Verify Qdrant has embedded data
- Check vector dimension matches
