#!/usr/bin/env python3
"""
Script to initialize the Qdrant collection for book content.
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.qdrant_service import QdrantService
from config.settings import settings


def setup_qdrant_collection():
    """
    Initialize the Qdrant collection for book content.
    """
    print("Setting up Qdrant collection...")
    
    try:
        qdrant_service = QdrantService()
        print(f"Successfully initialized collection: {settings.QDRANT_COLLECTION_NAME}")
        print("Qdrant collection setup complete!")
        return True
    except Exception as e:
        print(f"Error setting up Qdrant collection: {str(e)}")
        return False


if __name__ == "__main__":
    success = setup_qdrant_collection()
    if not success:
        sys.exit(1)