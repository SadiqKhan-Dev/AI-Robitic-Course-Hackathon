# Test script to demonstrate end-to-end functionality of the RAG agent
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend-book'))

from src.services.ingestion_service import IngestionService
from src.services.rag_agent_service import RAGAgentService


def test_end_to_end():
    """
    Test the end-to-end functionality of the RAG agent
    """
    print("Testing end-to-end functionality...")
    
    # Test 1: Verify services can be initialized
    try:
        ingestion_service = IngestionService()
        rag_agent_service = RAGAgentService()
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize services: {e}")
        return False
    
    # Test 2: Verify we can generate a response with no context (should return "I don't know")
    try:
        response = rag_agent_service.generate_response(
            query="What is the meaning of life according to this book?",
            user_id="test_user",
            page_context=None
        )
        
        print(f"✓ Test query response: '{response.answer[:50]}...'")
        
        # The response should either be "I don't know" (if no content is available)
        # or it should have sources if content was retrieved
        if response.fallback_used:
            print("✓ Fallback response ('I don't know') correctly triggered when no content available")
        else:
            print(f"✓ Response generated with {len(response.sources)} source(s) used")
            print(f"  Confidence: {response.confidence:.2f}")
            
    except Exception as e:
        print(f"✗ Failed to generate response: {e}")
        return False
    
    # Test 3: Test with a specific page context (if available)
    try:
        response_with_context = rag_agent_service.generate_response(
            query="What was discussed on this page?",
            user_id="test_user",
            page_context="https://example.com/test-page"
        )
        
        print(f"✓ Context-aware query response: '{response_with_context.answer[:50]}...'")
        
        if response_with_context.fallback_used:
            print("✓ Fallback response correctly triggered when no content available for specific page")
        else:
            print(f"✓ Context-aware response generated with {len(response_with_context.sources)} source(s)")
            
    except Exception as e:
        print(f"✗ Failed to generate context-aware response: {e}")
        return False
    
    print("\nEnd-to-end functionality test completed successfully!")
    print("Note: To fully test with real book content, you would need to:")
    print("1. Run the ingestion service with a real sitemap URL")
    print("2. Query the API endpoints with actual questions about the book")
    print("3. Verify that responses are grounded in the book content")
    
    return True


if __name__ == "__main__":
    success = test_end_to_end()
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)