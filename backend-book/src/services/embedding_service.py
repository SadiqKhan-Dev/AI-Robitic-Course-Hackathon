import cohere
from typing import List
from config.settings import settings


class EmbeddingService:
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)
        self.model = "embed-multilingual-v3.0"  # Using the multilingual model

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts using Cohere
        """
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"  # Using search_document for content chunks
        )
        
        return [embedding for embedding in response.embeddings]

    def create_query_embedding(self, query: str) -> List[float]:
        """
        Create embedding for a query using Cohere
        """
        response = self.client.embed(
            texts=[query],
            model=self.model,
            input_type="search_query"  # Using search_query for user queries
        )
        
        return response.embeddings[0]

    def create_embeddings_batch(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Create embeddings in batches to respect API limits
        Cohere's batch size limit is 96 texts per request
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.create_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings