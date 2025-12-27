#!/usr/bin/env python3
"""Validate embeddings in Qdrant and run test searches."""

import argparse
import asyncio
import json
import sys
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.services.vector_store import QdrantVectorStore
from src.services.embedder import CohereEmbedder
from src.utils.logger import setup_logging


async def validate_embeddings(config, test_queries: List[str], min_score: float = 0.7) -> dict:
    """Validate embeddings and run test searches.

    Args:
        config: Pipeline configuration
        test_queries: List of queries to search
        min_score: Minimum expected similarity score

    Returns:
        Dictionary with validation results
    """
    results = {
        "connection": False,
        "vector_count": 0,
        "test_queries": {},
        "all_passed": False,
        "error": None,
    }

    try:
        vector_store = QdrantVectorStore(config)
        embedder = CohereEmbedder(config)

        # Test connection
        results["connection"] = await vector_store.connect()
        if not results["connection"]:
            raise ConnectionError("Failed to connect to Qdrant")

        # Count vectors
        results["vector_count"] = await vector_store.count_vectors()

        if results["vector_count"] == 0:
            results["error"] = "No vectors found in collection"
            return results

        # Run test searches
        test_results = await vector_store.test_search(test_queries, embedder)

        for query, result in test_results.items():
            if "error" in result:
                results["test_queries"][query] = {"passed": False, "error": result["error"]}
            else:
                passed = result["found"] and result["top_score"] >= min_score
                results["test_queries"][query] = {
                    "passed": passed,
                    "found": result["found"],
                    "top_score": result["top_score"],
                    "result_count": result["result_count"],
                }

        # Determine overall pass/fail
        all_passed = all(
            r.get("passed", False) for r in results["test_queries"].values()
        )
        results["all_passed"] = all_passed

        return results

    except Exception as e:
        results["error"] = str(e)
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate embeddings in Qdrant")
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
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.7,
        help="Minimum expected similarity score",
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

    # Default test queries for the AI Robotic Course
    test_queries = [
        "ROS 2 robotics framework",
        "NVIDIA Isaac integration",
        "Vision Language Action models",
    ]

    print("Validating embeddings in Qdrant...")
    print(f"  Collection: {config.qdrant_collection}")
    print(f"  Test queries: {len(test_queries)}")
    print()

    results = asyncio.run(validate_embeddings(config, test_queries, args.min_score))

    if args.json:
        print(json.dumps(results))
    else:
        if results["error"]:
            print(f"Error: {results['error']}")
            sys.exit(1)

        print("=" * 50)
        print("Embedding Validation Results")
        print("=" * 50)
        print(f"  Connected:       {'Yes' if results['connection'] else 'No'}")
        print(f"  Vector count:    {results['vector_count']}")
        print()

        print("Test Queries:")
        for query, result in results["test_queries"].items():
            status = "PASS" if result.get("passed") else "FAIL"
            print(f"  [{status}] \"{query}\"")
            print(f"        Found: {result.get('found', False)}, Top score: {result.get('top_score', 0):.3f}")
            if "error" in result:
                print(f"        Error: {result['error']}")
        print()

        if results["all_passed"]:
            print("Status: VALID - All test queries passed")
            sys.exit(0)
        else:
            print("Status: INVALID - Some tests failed")
            sys.exit(1)
