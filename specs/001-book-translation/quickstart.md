# Quickstart Guide: Book Translation Feature

## Overview
This guide will help you quickly set up and run the book translation feature that allows users to translate book content into multiple languages while preserving technical accuracy and structure.

## Prerequisites
- Node.js (v16 or higher)
- Python (v3.11 or higher)
- Docusaurus CLI installed globally: `npm install -g @docusaurus/core@latest`
- An LLM service account (OpenAI, Azure OpenAI, or similar)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Backend Dependencies
```bash
cd backend-book
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `backend-book` directory:
```env
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.openai.com/v1  # or your LLM provider's base URL
LLM_MODEL_NAME=gpt-4-turbo  # or your preferred model
```

### 4. Install Frontend Dependencies
```bash
cd frontend-book
npm install
```

### 5. Run the Backend Service
```bash
cd backend-book
python -m src.main
```
The backend service will start on `http://localhost:8000`.

### 6. Run the Frontend Development Server
```bash
cd frontend-book
npm start
```
The Docusaurus site will start on `http://localhost:3000`.

## Usage

### Translating Book Content
1. Navigate to any book page in the Docusaurus UI
2. Use the translation controls to select a target language
3. The content will be translated while preserving code blocks and technical terms

### Translating Selected Text
1. Select a portion of text within a book page
2. Use the selection-based translation option
3. Only the selected text will be translated while maintaining document structure

## API Endpoints
- `POST /api/v1/translation` - Main translation endpoint
- `GET /api/v1/translation/supported-languages` - Get supported languages
- `POST /api/v1/translation/selection` - Translate selected text

## Configuration Options
- `TRANSLATION_PRESERVE_CODE_BLOCKS` (default: true) - Whether to preserve code blocks unchanged
- `TRANSLATION_PRESERVE_TECHNICAL_TERMS` (default: true) - Whether to preserve/translate technical terms appropriately
- `TRANSLATION_TIMEOUT_MS` (default: 30000) - Request timeout in milliseconds

## Troubleshooting
- If translations are not appearing, check that your LLM API key is valid and has sufficient quota
- If code blocks are not being preserved, ensure the `preserve_code_blocks` parameter is set to true
- For performance issues with large documents, consider breaking content into smaller sections