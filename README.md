# AI Robotic Course Hackathon - Book Translation Feature

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator, enhanced with a book translation feature that allows users to translate content into multiple languages while preserving technical accuracy.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Backend Translation Service

The translation feature requires a backend service for processing translations:

1. Navigate to the backend directory:
```bash
cd backend-book
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env to add your LLM API key
```

5. Run the backend service:
```bash
python -m src.main
```

## Translation Feature

The book translation feature allows users to:
- Translate book content into multiple languages (Spanish, French, Arabic, Urdu)
- Preserve technical terms, code blocks, and file names during translation
- Translate selected text portions while maintaining document structure
- Switch between multiple target languages
- Compare translations across different languages

### How to Use
1. Navigate to any book page in the Docusaurus UI
2. Use the translation controls to select a target language
3. The content will be translated while preserving code blocks and technical terms
4. Use the toggle to switch between original and translated content

### Technical Implementation
- **Backend**: FastAPI service with LLM integration (OpenAI or configurable provider)
- **Frontend**: Docusaurus theme component with React UI
- **Preservation**: Pre/post-processing approach to identify and preserve technical elements
- **Quality**: Validation checks to ensure technical elements remain unchanged (95%+ preservation rate)

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
