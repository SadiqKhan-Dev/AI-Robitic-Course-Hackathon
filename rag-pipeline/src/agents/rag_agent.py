"""RAG Agent using Gemini for reasoning."""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Add rag-pipeline to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RAGAgent:
    """RAG Agent that uses Gemini for intelligent responses."""

    def __init__(self, config_path: str = None):
        """Initialize RAG Agent."""
        # Load config
        if config_path is None:
            config_path = PROJECT_ROOT / "config.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize services
        self._init_services()

        # Define system prompt
        self.system_prompt = self._create_system_prompt()

    def _init_services(self):
        """Initialize embedding and LLM services."""
        from src.services.embedding_service import (
            EmbeddingService,
            GeminiLLMService,
        )
        from src.services.qdrant_service import QdrantService

        # Qdrant service
        self.qdrant_service = QdrantService()

        # Embedding service
        self.embedding_service = EmbeddingService()

        # Gemini LLM service
        self.gemini_service = GeminiLLMService()

        # RAG config
        self.top_k = self.config["rag"].get("top_k", 5)
        self.similarity_threshold = self.config["rag"].get("similarity_threshold", 0.5)
        self.context_window = self.config["rag"].get("context_window", 4000)

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are a helpful AI assistant specialized in the AI Robotics Book.
Your goal is to answer questions about the book content by searching the knowledge base.

When answering questions:
1. First, search for relevant information using the search tool
2. Review the retrieved context
3. Provide a clear, helpful answer based on the context
4. If the context doesn't contain enough information, say so

You are helpful, precise, and always cite your sources from the book."""

    def search_knowledge_base(self, query: str) -> str:
        """Search the knowledge base and return formatted results."""
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Search Qdrant
        results = self.qdrant_service.search(
            query_vector=query_embedding,
            top_k=self.top_k,
            score_threshold=self.similarity_threshold,
        )

        if not results:
            return "No relevant information found in the knowledge base."

        # Format results
        context_parts = []
        for i, result in enumerate(results, 1):
            payload = result.get("payload", {})
            title = payload.get("title", "Unknown")
            text = payload.get("text", "")
            url = payload.get("url", "")
            score = result.get("score", 0)

            context_parts.append(
                f"[Source {i}] (relevance: {score:.2f})\n"
                f"Title: {title}\n"
                f"Content: {text}\n"
                f"URL: {url}"
            )

        return "\n\n".join(context_parts)

    def generate_response(self, question: str) -> Dict[str, Any]:
        """Generate a response to a question using RAG."""
        # Step 1: Search knowledge base
        context = self.search_knowledge_base(question)

        # Step 2: Generate response with Gemini
        response = self.gemini_service.generate_rag_response(
            question=question,
            context=context,
            system_prompt=self.system_prompt,
        )

        return {
            "question": question,
            "answer": response,
            "context": context,
            "sources": [
                {
                    "title": r.get("payload", {}).get("title", "Unknown"),
                    "url": r.get("payload", {}).get("url", ""),
                    "score": r.get("score", 0),
                }
                for r in self.qdrant_service.search(
                    self.embedding_service.embed_query(question),
                    top_k=self.top_k,
                )
            ],
        }

    def chat(self, message: str) -> str:
        """Simple chat interface."""
        result = self.generate_response(message)
        return result["answer"]


def get_rag_agent(config_path: str = None) -> RAGAgent:
    """Factory function to get RAG agent."""
    return RAGAgent(config_path)


if __name__ == "__main__":
    # Test the RAG agent
    agent = get_rag_agent()

    print("=" * 60)
    print("RAG Agent - AI Robotics Book Assistant")
    print("=" * 60)
    print("\nAsk me anything about the AI Robotics Book!")
    print("(Type 'quit' to exit)\n")

    while True:
        question = input("You: ")
        if question.lower() in ["quit", "exit", "q"]:
            break

        print("\nThinking...")
        response = agent.generate_response(question)

        print(f"\nAssistant: {response['answer']}")
        print(f"\n[Sources: {len(response['sources'])} found]")
