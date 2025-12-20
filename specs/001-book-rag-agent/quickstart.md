# Quickstart Guide: Floating RAG-Powered AI Agent for Book Content

## Overview
This guide provides instructions to quickly set up and run the RAG-powered AI agent for book content.

## Prerequisites

1. **Python 3.11+** installed on your system
2. **Node.js 18+** for frontend development
3. **Access to Cohere API** for embeddings
4. **Qdrant Cloud account** (free tier available)
5. **OpenAI API access** (or compatible provider) for the agent
6. **Book sitemap URL** for content ingestion

## Setup Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-robotic-book
```

### 2. Set up Backend Environment
```bash
# Navigate to backend directory
cd backend-book

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Set up Frontend Environment
```bash
# Navigate to frontend directory
cd frontend-book

# Install dependencies
npm install
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend-book` directory with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_HOST=your_qdrant_cluster_url
OPENAI_API_KEY=your_openai_api_key  # or compatible provider
BOOK_SITEMAP_URL=https://your-book-site.com/sitemap.xml
```

### 5. Initialize Vector Database
```bash
# From backend-book directory
python scripts/setup_qdrant.py
```

### 6. Ingest Book Content
```bash
# From backend-book directory
python -m src.services.ingestion_service --sitemap-url $BOOK_SITEMAP_URL
```

## Running the Application

### 1. Start the Backend API
```bash
# From backend-book directory
uvicorn src.api.main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
# From frontend-book directory
npm run start
```

### 3. Access the Application
- Frontend: `http://localhost:3000` (or your Docusaurus configured port)
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Testing the RAG Agent

1. Navigate to any book page in the frontend
2. Open the floating RAG agent UI (usually a chat icon in the corner)
3. Ask a question about the book content
4. The agent should respond with information grounded in the book content
5. If the answer isn't in the book, it should respond with "I don't know"

## API Endpoints

### Ingestion
- `POST /ingest` - Trigger content ingestion from sitemap
- `POST /ingest/sitemap` - Ingest content from a specific sitemap URL

### Query/Retrieval
- `POST /query` - Submit a question and get a response
- `POST /query/page` - Submit a question with page context

### Health
- `GET /health` - Check API health status

## Troubleshooting

### Common Issues

1. **"No content found in Qdrant"**
   - Ensure the ingestion process completed successfully
   - Check your sitemap URL is accessible and properly formatted
   - Verify your Cohere and Qdrant configurations

2. **"Embedding generation failed"**
   - Check your Cohere API key is valid
   - Ensure you have sufficient API quota

3. **"Qdrant connection failed"**
   - Verify your Qdrant host URL and API key
   - Check if your Qdrant Cloud instance is running

### Useful Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Test a query directly
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this book about?", "page_context": null}'
```

## Next Steps

1. Customize the frontend UI to match your book's design
2. Add more sophisticated text chunking strategies
3. Implement query analytics and feedback collection
4. Set up automated content updates when the book content changes