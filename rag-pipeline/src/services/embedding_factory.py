"""Multi-Provider Embedding Service Factory."""
import os
from pathlib import Path
from typing import List, Optional, Union

import yaml


class EmbeddingProvider:
    """Base class for embedding providers."""

    def __init__(self, config: dict):
        self.config = config

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def get_dimension(self) -> int:
        raise NotImplementedError


class SentenceTransformersProvider(EmbeddingProvider):
    """Free embeddings using sentence-transformers (HuggingFace)."""

    def __init__(self, config: dict):
        super().__init__(config)
        from sentence_transformers import SentenceTransformer

        model_name = config.get("model", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.model_name = model_name
        print(f"Loaded SentenceTransformer: {model_name} (dim={self.dimension})")

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def get_dimension(self) -> int:
        return self.dimension


class CohereProvider(EmbeddingProvider):
    """Cohere embeddings (requires API key)."""

    def __init__(self, config: dict):
        super().__init__(config)
        try:
            import cohere
            api_key = config.get("api_key")
            if not api_key or api_key == "YOUR_COHERE_API_KEY":
                raise ValueError("Cohere API key not configured")
            self.client = cohere.Client(api_key)
            self.model = config.get("model", "embed-english-v3.0")
            self.dimension = 1024  # embed-english-v3.0
            print(f"Loaded Cohere: {self.model} (dim={self.dimension})")
        except ImportError:
            raise ImportError("Please install cohere: pip install cohere")

    def embed(self, text: str) -> List[float]:
        response = self.client.embed(texts=[text], model=self.model)
        return response.embeddings[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embed(texts=texts, model=self.model)
        return response.embeddings

    def get_dimension(self) -> int:
        return self.dimension


class HuggingFaceProvider(EmbeddingProvider):
    """HuggingFace Inference API embeddings."""

    def __init__(self, config: dict):
        super().__init__(config)
        api_key = config.get("api_key", "")
        self.model = config.get("model", "sentence-transformers/all-MiniLM-L6-v2")
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.dimension = 384  # all-MiniLM-L6-v2
        print(f"Loaded HuggingFace: {self.model}")

    def embed(self, text: str) -> List[float]:
        import requests

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": text, "truncate": 512}
        )
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback to local
            raise RuntimeError(f"HuggingFace API error: {response.text}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Batch through API
        import requests

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": texts, "truncate": 512}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(f"HuggingFace API error: {response.text}")

    def get_dimension(self) -> int:
        return self.dimension


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embeddings."""

    def __init__(self, config: dict):
        super().__init__(config)
        try:
            import openai
            api_key = config.get("api_key")
            if not api_key or api_key == "YOUR_OPENAI_API_KEY":
                raise ValueError("OpenAI API key not configured")
            self.client = openai.OpenAI(api_key=api_key)
            self.model = config.get("model", "text-embedding-3-small")
            self.dimension = config.get("dimension", 1536)
            print(f"Loaded OpenAI: {self.model} (dim={self.dimension})")
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [d.embedding for d in response.data]

    def get_dimension(self) -> int:
        return self.dimension


# Provider factory
def get_embedding_provider(provider: str = "sentence-transformers", config_path: str = None) -> EmbeddingProvider:
    """Get embedding provider by name."""

    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    with open(config_path, "r") as f:
        full_config = yaml.safe_load(f)

    # Get provider config
    if provider == "cohere":
        config = full_config.get("cohere", {})
        return CohereProvider(config)
    elif provider == "huggingface":
        config = full_config.get("huggingface", {})
        return HuggingFaceProvider(config)
    elif provider == "openai":
        config = full_config.get("openai", {})
        return OpenAIProvider(config)
    else:
        # Default to sentence-transformers (free)
        config = full_config.get("embedding", {})
        return SentenceTransformersProvider(config)


if __name__ == "__main__":
    # Test all providers
    config_path = Path(__file__).parent.parent.parent / "config.yaml"

    print("Testing embedding providers...\n")

    # Test sentence-transformers (free)
    print("1. SentenceTransformers (Free):")
    provider = get_embedding_provider("sentence-transformers", config_path)
    test = provider.embed("Hello world")
    print(f"   Dimension: {len(test)}")
    print(f"   First 5 values: {test[:5]}")

    # Test Cohere (requires API key)
    print("\n2. Cohere:")
    try:
        provider = get_embedding_provider("cohere", config_path)
        print(f"   Loaded: {provider.model}")
    except ValueError as e:
        print(f"   Not configured: {e}")
    except ImportError as e:
        print(f"   Not installed: {e}")

    print("\nDone!")
