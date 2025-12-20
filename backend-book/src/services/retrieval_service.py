from typing import List, Dict, Optional
from src.services.qdrant_service import QdrantService
from src.services.embedding_service import EmbeddingService
from config.settings import settings
import logging


class RetrievalService:
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        self.logger = logging.getLogger(__name__)

    def retrieve_relevant_content(self, query: str, top_k: int = None, page_url: Optional[str] = None) -> List[Dict]:
        """
        Retrieve the most relevant content chunks for a given query
        """
        if top_k is None:
            top_k = settings.TOP_K

        try:
            # 1. Create embedding for the query
            query_embedding = self.embedding_service.create_query_embedding(query)
            
            # 2. Search in Qdrant
            results = self.qdrant_service.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                page_url=page_url
            )
            
            # 3. Filter results by minimum relevance score if configured
            if settings.MIN_RELEVANCE_SCORE > 0:
                results = [
                    result for result in results 
                    if result['score'] >= settings.MIN_RELEVANCE_SCORE
                ]
            
            self.logger.info(f"Retrieved {len(results)} relevant chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving content for query '{query}': {str(e)}")
            return []

    def get_content_by_ids(self, content_ids: List[str]) -> List[Dict]:
        """
        Retrieve specific content chunks by their IDs
        """
        try:
            # For now, we'll use search with filters to get specific IDs
            # In a real implementation, we might use a different method to retrieve by ID
            all_docs = self.qdrant_service.get_all_documents()
            filtered_docs = [doc for doc in all_docs if doc['id'] in content_ids]
            
            return filtered_docs
        except Exception as e:
            self.logger.error(f"Error retrieving content by IDs: {str(e)}")
            return []

    def retrieve_for_global_query(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve content for queries that span the entire book
        """
        return self.retrieve_relevant_content(query, top_k, page_url=None)

    def retrieve_for_page_context(self, query: str, page_url: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve content prioritizing the current page context
        """
        return self.retrieve_relevant_content(query, top_k, page_url=page_url)