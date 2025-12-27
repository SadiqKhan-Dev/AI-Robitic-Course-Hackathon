"""Upload CLI command for storing embeddings in Qdrant."""

import argparse
import asyncio
import json
import sys

from ..config import load_config
from ..services.vector_store import QdrantVectorStore, load_embeddings_for_upload
from ..services.state_manager import StateManager
from ..utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Upload embeddings to Qdrant vector database"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate the collection (deletes existing data)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous upload state",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./data/embeddings.jsonl",
        help="Input embeddings file path",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for uploads",
    )
    return parser.parse_args()


def main():
    """Main entry point for upload command."""
    args = parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(
        level=log_level,
        json_output=args.json,
    )

    # Load configuration
    try:
        config = load_config()
        config.ensure_dirs()
    except Exception as e:
        logger.error("config_load_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)

    logger.info("upload_started", collection=config.qdrant_collection)

    # Initialize components
    vector_store = QdrantVectorStore(config)
    state_manager = StateManager(config)

    async def run_upload():
        # Test connection
        connected = await vector_store.connect()
        if not connected:
            raise ConnectionError("Failed to connect to Qdrant")

        # Create or connect to collection
        created = await vector_store.create_collection(recreate=args.recreate)
        logger.info("collection_ready", created=created)

        # Load embeddings
        embeddings = load_embeddings_for_upload(args.input)
        logger.info("embeddings_loaded", count=len(embeddings))

        if not embeddings:
            logger.warning("no_embeddings_found", input=args.input)
            return {
                "embeddings_loaded": 0,
                "vectors_uploaded": 0,
                "vectors_failed": 0,
            }

        # Resume state
        upload_state = state_manager.get_upload_state()
        if args.resume and upload_state.vectors_uploaded:
            uploaded_set = set(upload_state.vectors_uploaded)
            embeddings = [e for e in embeddings if e.chunk_id not in uploaded_set]
            logger.info(
                "resuming_upload",
                skipped=upload_state.completed_vectors,
                remaining=len(embeddings),
            )

        if not embeddings:
            logger.info("nothing_to_upload")
            return {
                "embeddings_loaded": len(embeddings),
                "vectors_uploaded": 0,
                "vectors_failed": 0,
            }

        # Upload embeddings
        def progress_callback(current, total):
            if current % 500 == 0:
                logger.info("upload_progress", current=current, total=total)

        uploaded_ids, failed = await vector_store.upload_embeddings(
            embeddings, progress_callback
        )

        # Update and save state
        upload_state.mark_uploaded(uploaded_ids)
        for vector_id, error in failed.items():
            upload_state.mark_failed(vector_id, error)
        state_manager.save_state("upload")

        # Get final count
        total_count = await vector_store.count_vectors()

        return {
            "embeddings_loaded": len(embeddings),
            "vectors_uploaded": len(uploaded_ids),
            "vectors_failed": len(failed),
            "total_vectors_in_collection": total_count,
        }

    try:
        result = asyncio.run(run_upload())

        if args.json:
            print(json.dumps(result))
        else:
            print("\n" + "=" * 50)
            print("Upload Complete")
            print("=" * 50)
            print(f"  Embeddings loaded:   {result['embeddings_loaded']}")
            print(f"  Vectors uploaded:    {result['vectors_uploaded']}")
            print(f"  Vectors failed:      {result['vectors_failed']}")
            print(f"  Total in collection: {result['total_vectors_in_collection']}")
            print("=" * 50)

        sys.exit(0 if result["vectors_failed"] == 0 else 1)

    except KeyboardInterrupt:
        logger.info("upload_cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        asyncio.run(vector_store.close())


if __name__ == "__main__":
    main()
