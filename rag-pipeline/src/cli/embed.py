"""Embed CLI command for generating embeddings."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from ..config import load_config
from ..models.document import DocumentPage
from ..services.chunker import TextChunker
from ..services.embedder import CohereEmbedder, save_embeddings_to_jsonl
from ..services.state_manager import StateManager
from ..utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate embeddings for crawled content"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Chunk size in tokens (default: 512)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        help="Chunk overlap in tokens (default: 50)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous embed state",
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
        "--max-chunks",
        type=int,
        default=None,
        help="Maximum number of chunks to process",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./data/embeddings.jsonl",
        help="Output file path",
    )
    return parser.parse_args()


def load_cached_documents(cache_dir: str = "./data/cache/extracted") -> list[DocumentPage]:
    """Load documents from cached files.

    Args:
        cache_dir: Directory containing cached content

    Returns:
        List of DocumentPage instances
    """
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        return []

    documents = []
    for meta_path in cache_path.glob("*.meta.json"):
        try:
            # Load metadata
            metadata = json.loads(meta_path.read_text())
            # Fix: Replace .meta.json with .txt instead of using with_suffix
            text_path = Path(str(meta_path).replace(".meta.json", ".txt"))

            if not text_path.exists():
                continue

            text_content = text_path.read_text(encoding="utf-8")

            doc = DocumentPage(
                url=metadata.get("url", ""),
                title=metadata.get("title", ""),
                extracted_text=text_content,
                crawled_at=metadata.get("crawled_at", ""),
                content_hash=metadata.get("content_hash", ""),
                metadata=metadata.get("metadata", {}),
            )
            documents.append(doc)

        except Exception as e:
            print(f"Warning: Failed to load {meta_path}: {e}")

    return documents


def main():
    """Main entry point for embed command."""
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

        # Override chunking settings if provided
        if args.chunk_size:
            config.chunk_size = args.chunk_size
        if args.chunk_overlap:
            config.chunk_overlap = args.chunk_overlap

        config.ensure_dirs()
    except Exception as e:
        logger.error("config_load_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)

    logger.info("embed_started", chunk_size=config.chunk_size, overlap=config.chunk_overlap)

    # Initialize components
    chunker = TextChunker(config)
    embedder = CohereEmbedder(config)
    state_manager = StateManager(config)

    async def run_embed():
        # Load cached documents
        documents = load_cached_documents(str(Path(config.cache_dir) / "extracted"))
        logger.info("documents_loaded", count=len(documents))

        if not documents:
            logger.warning("no_documents_found", cache_dir=config.cache_dir)
            return {
                "documents_loaded": 0,
                "chunks_created": 0,
                "embeddings_generated": 0,
            }

        # Chunk documents
        all_chunks, chunk_counts = chunker.chunk_documents(documents)
        logger.info("chunks_created", total=len(all_chunks))

        # Resume state
        embed_state = state_manager.get_embed_state()
        if args.resume and embed_state.chunks_processed:
            processed_set = set(embed_state.chunks_processed)
            all_chunks = [c for c in all_chunks if c.chunk_id not in processed_set]
            logger.info(
                "resuming_embed",
                skipped=embed_state.completed_chunks,
                remaining=len(all_chunks),
            )

        # Limit chunks if specified
        if args.max_chunks:
            all_chunks = all_chunks[:args.max_chunks]

        # Generate embeddings
        def progress_callback(current, total):
            if current % 100 == 0:
                logger.info("embedding_progress", current=current, total=total)

        embeddings = await embedder.embed_chunks(all_chunks, progress_callback)

        # Save embeddings
        save_embeddings_to_jsonl(embeddings, args.output)

        # Update and save state
        embed_state.mark_processed([e.chunk_id for e in embeddings])
        state_manager.save_state("embed")

        return {
            "documents_loaded": len(documents),
            "chunks_created": len(all_chunks),
            "embeddings_generated": len(embeddings),
            "output_path": args.output,
        }

    try:
        result = asyncio.run(run_embed())

        if args.json:
            print(json.dumps(result))
        else:
            print("\n" + "=" * 50)
            print("Embed Complete")
            print("=" * 50)
            print(f"  Documents loaded:  {result['documents_loaded']}")
            print(f"  Chunks created:    {result['chunks_created']}")
            print(f"  Embeddings saved:  {result['embeddings_generated']}")
            print(f"  Output file:       {result['output_path']}")
            print("=" * 50)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("embed_cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("embed_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        asyncio.run(embedder.close())


if __name__ == "__main__":
    main()
