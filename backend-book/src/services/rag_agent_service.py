from typing import List, Dict, Optional
from src.services.retrieval_service import RetrievalService
from src.models.response import Response
from config.settings import settings
import openai
import uuid
import logging


class RAGAgentService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY

    def generate_response(self, query: str, user_id: str, page_context: Optional[str] = None) -> Response:
        """
        Generate a response to a user query using retrieved context
        """
        try:
            # 1. Retrieve relevant content based on query and context
            if page_context:
                retrieved_chunks = self.retrieval_service.retrieve_for_page_context(
                    query, page_context
                )
            else:
                retrieved_chunks = self.retrieval_service.retrieve_for_global_query(query)
            
            # 2. Check if we have sufficient context
            if not retrieved_chunks:
                self.logger.info(f"No relevant content found for query: {query}")
                return Response(
                    id=str(uuid.uuid4()),
                    query_id="",  # Will be set by caller
                    answer="I don't know",
                    sources=[],
                    confidence=0.0,
                    fallback_used=True
                )
            
            # 3. Format the retrieved context for the LLM
            context_text = self._format_context_for_llm(retrieved_chunks)
            
            # 4. Generate response using the LLM with the retrieved context
            answer = self._generate_answer_with_context(query, context_text)
            
            # 5. Create and return the response object
            response = Response(
                id=str(uuid.uuid4()),
                query_id="",  # Will be set by caller
                answer=answer,
                sources=[chunk['id'] for chunk in retrieved_chunks],
                confidence=max([chunk['score'] for chunk in retrieved_chunks]),  # Use highest score
                fallback_used=False
            )
            
            self.logger.info(f"Generated response for query: {query[:50]}...")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response for query '{query}': {str(e)}")
            return Response(
                id=str(uuid.uuid4()),
                query_id="",  # Will be set by caller
                answer="I don't know",
                sources=[],
                confidence=0.0,
                fallback_used=True
            )

    def _format_context_for_llm(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format the retrieved chunks into a context string for the LLM
        """
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(
                f"Source {i+1} (from {chunk['url']}):\n{chunk['content']}\n"
            )
        
        return "\n".join(context_parts)

    def _generate_answer_with_context(self, query: str, context: str) -> str:
        """
        Generate an answer using the LLM with the provided context
        """
        # Create the prompt for the LLM
        prompt = f"""
        You are an AI assistant for a book. Answer the user's question based ONLY on the provided context.
        If the answer is not available in the context, respond with "I don't know".
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        
        try:
            # Using OpenAI's API to generate the response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # This can be configured based on settings
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an AI assistant that answers questions based only on the provided context. If the answer is not in the context, respond with 'I don't know'. Be concise and accurate."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent, factual responses
            )
            
            answer = response.choices[0].message['content'].strip()
            
            # Ensure the agent adheres to the "I don't know" rule
            if "i don't know" in answer.lower() or "unable to find" in answer.lower():
                return "I don't know"
            
            return answer
        except Exception as e:
            self.logger.error(f"Error calling LLM: {str(e)}")
            return "I don't know"

    def validate_response_accuracy(self, response: Response, query: str) -> bool:
        """
        Validate that the response is grounded in the provided sources
        This is a basic implementation - in a real system, you might do more sophisticated validation
        """
        # For now, just return True if the response wasn't a fallback
        return not response.fallback_used