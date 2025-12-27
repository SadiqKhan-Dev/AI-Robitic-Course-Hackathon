"""Embedding Service using Sentence Transformers (Free) and Gemini for LLM."""
import os
import sys
from pathlib import Path
from typing import Any, List

import yaml
from sentence_transformers import SentenceTransformer

# Add rag-pipeline to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers (free)."""

    def __init__(self, config_path: str = None):
        """Initialize embedding service."""
        # Load config
        if config_path is None:
            config_path = PROJECT_ROOT / "config.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Use free sentence-transformers model
        # all-MiniLM-L6-v2 is fast, free, and produces 384-dim vectors
        self.model_name = self.config["embedding"].get(
            "model", "all-MiniLM-L6-v2"
        )
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        print(f"Loaded embedding model: {self.model_name}")
        print(f"Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.model.encode(text).tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query (same as embed_text)."""
        return self.embed_text(query)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self.model.encode(texts).tolist()

    def get_dimension(self) -> int:
        """Return embedding dimension."""
        return self.dimension


class GeminiLLMService:
    """Service for generating responses using Gemini (free tier)."""

    def __init__(self, config_path=None):
        """Initialize Gemini LLM service."""
        import google.generativeai as genai

        # Load config
        if config_path is None:
            config_path = PROJECT_ROOT / "config.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Get API key
        api_key = self.config["gemini"]["api_key"]
        if api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError(
                "Please set your GEMINI_API_KEY in config.yaml. "
                "Get it from https://aistudio.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)

        self.model_name = self.config["gemini"].get("model", "gemini-1.5-flash")
        self.temperature = self.config["gemini"].get("temperature", 0.3)
        self.max_output_tokens = self.config["gemini"].get("max_output_tokens", 2048)

        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
            },
        )

        print(f"Loaded Gemini model: {self.model_name}")

    def generate_response(
        self, prompt: str, system_prompt: str = None
    ) -> str:
        """Generate response from Gemini."""
        import google.generativeai as genai

        try:
            if system_prompt:
                # Gemini uses history-based prompting
                response = self.model.generate_content(
                    [system_prompt, prompt]
                )
            else:
                response = self.model.generate_content(prompt)

            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: {str(e)}"

    def generate_rag_response(
        self, question: str, context: str, system_prompt: str = None
    ) -> str:
        """Generate RAG response with context."""
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant for the AI Robotics Book.
Use the provided context to answer the user's question.
If the answer is not in the context, say "I don't have enough information to answer that question."
Keep your answers clear and concise."""

        rag_prompt = f"""Context:
{context}

Question: {question}

Please provide a helpful answer based on the context above."""

        return self.generate_response(rag_prompt, system_prompt)


def get_embedding_service(config_path: str = None) -> EmbeddingService:
    """Factory function to get embedding service."""
    return EmbeddingService(config_path)


def get_gemini_service(config_path: str = None) -> GeminiLLMService:
    """Factory function to get Gemini LLM service."""
    return GeminiLLMService(config_path)


if __name__ == "__main__":
    # Test embedding service
    print("Testing Embedding Service...")
    embed_service = get_embedding_service()
    test_text = "Hello, this is a test embedding"
    embedding = embed_service.embed_text(test_text)
    print(f"Embedding generated: {len(embedding)} dimensions")

    # Test Gemini (requires API key)
    print("\nTesting Gemini Service...")
    try:
        gemini_service = get_gemini_service()
        response = gemini_service.generate_response("Hello, are you working?")
        print(f"Gemini response: {response}")
    except ValueError as e:
        print(f"Gemini not configured: {e}")
