#!/usr/bin/env python3
"""Setup Qdrant collection for the RAG pipeline."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.utils.logger import setup_logging


async def setup_collection(config, recreate: bool = False) -> dict:
    """Setup the Qdrant collection.

    Args:
        config: Pipeline configuration
        recreate: Whether to recreate if exists

    Returns:
        Dictionary with setup results
    """
    from src.services.vector_store import QdrantVectorStore

    vector_store = QdrantVectorStore(config)

    results = {
        "connected": False,
        "collection_created": False,
        "collection_info": None,
        "error": None,
    }

    try:
        # Test connection
        results["connected"] = await vector_store.connect()
        if not results["connected"]:
            raise ConnectionError("Failed to connect to Qdrant")

        # Create collection
        results["collection_created"] = await vector_store.create_collection(recreate=recreate)

        # Get collection info
        client = await vector_store._get_client()
        collection_name = config.qdrant_collection

        try:
            collection_info = await client.get_collection(collection_name)
            results["collection_info"] = {
                "name": collection_name,
                "vectors_count": collection_info.vectors_count,
                "dimension": collection_info.config.params.size,
                "distance": str(collection_info.config.params.distance),
            }
        except Exception:
            # Collection might be empty
            results["collection_info"] = {
                "name": collection_name,
                "vectors_count": 0,
                "dimension": config.embedding_dimensions,
                "distance": "COSINE",
            }

        return results

    except Exception as e:
        results["error"] = str(e)
        return results
    finally:
        await vector_store.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Setup Qdrant collection")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate the collection (deletes existing data)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = main()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(level=log_level)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    print("Setting up Qdrant collection...")
    print(f"  URL: {config.qdrant_url}")
    print(f"  Collection: {config.qdrant_collection}")
    print(f"  Dimensions: {config.embedding_dimensions}")
    print()

    results = asyncio.run(setup_collection(config, recreate=args.recreate))

    if args.json:
        print(json.dumps(results))
    else:
        if results["error"]:
            print(f"Error: {results['error']}")
            sys.exit(1)

        print("=" * 50)
        print("Qdrant Setup Results")
        print("=" * 50)
        print(f"  Connected:         {'Yes' if results['connected'] else 'No'}")
        print(f"  Collection Created: {'Yes' if results['collection_created'] else 'No'}")
        if results["collection_info"]:
            info = results["collection_info"]
            print(f"  Name:              {info['name']}")
            print(f"  Vectors:           {info['vectors_count']}")
            print(f"  Dimension:         {info['dimension']}")
            print(f"  Distance:          {info['distance']}")
        print("=" * 50)

        if results["connected"]:
            print("Status: READY")
            sys.exit(0)
        else:
            print("Status: FAILED")
            sys.exit(1)
