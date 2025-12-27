"""Pipeline CLI - Orchestrates the complete RAG ingestion pipeline."""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent

from ..config import load_config
from ..services.crawler import DocusaurusCrawler
from ..services.extractor import DocusaurusContentExtractor
from ..services.chunker import TextChunker
from ..services.embedder import CohereEmbedder, save_embeddings_to_jsonl
from ..services.vector_store import QdrantVectorStore, load_embeddings_for_upload
from ..services.state_manager import StateManager
from ..utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the complete RAG ingestion pipeline"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to crawl",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous pipeline state",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate Qdrant collection (deletes existing data)",
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
        "--skip-crawl",
        action="store_true",
        help="Skip crawl phase (use cached content)",
    )
    parser.add_argument(
        "--skip-embed",
        action="store_true",
        help="Skip embed phase (use cached embeddings)",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip upload phase (don't upload to Qdrant)",
    )
    return parser.parse_args()


def load_cached_documents(cache_dir: str = "./data/cache/extracted") -> list:
    """Load documents from cached files."""
    from ..models.document import DocumentPage
    import json
    import structlog
    logger = structlog.get_logger(__name__)

    cache_path = Path(cache_dir)
    logger.debug("load_cached_documents", cache_dir=cache_dir, path_exists=cache_path.exists())
    if not cache_path.exists():
        logger.debug("cache_path_not_found", path=str(cache_path))
        return []

    meta_files = list(cache_path.glob("*.meta.json"))
    logger.debug("meta_files_found", count=len(meta_files))
    documents = []
    for meta_path in meta_files:
        try:
            metadata = json.loads(meta_path.read_text())
            text_path = Path(str(meta_path).replace(".meta.json", ".txt"))
            if text_path.exists():
                doc = DocumentPage(
                    url=metadata.get("url", ""),
                    title=metadata.get("title", ""),
                    extracted_text=text_path.read_text(encoding="utf-8"),
                    crawled_at=metadata.get("crawled_at", ""),
                    content_hash=metadata.get("content_hash", ""),
                    metadata=metadata.get("metadata", {}),
                )
                documents.append(doc)
        except Exception as e:
            logger.error("document_load_failed", path=str(meta_path), error=str(e))

    return documents


class PipelineStats:
    """Track pipeline statistics."""

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.phases = {
            "crawl": {"started": None, "completed": None, "pages": 0},
            "embed": {"started": None, "completed": None, "chunks": 0, "embeddings": 0},
            "upload": {"started": None, "completed": None, "vectors": 0},
        }
        self.errors = []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "duration_seconds": duration,
            "phases": self.phases,
            "errors": self.errors,
        }


def main():
    """Main entry point for pipeline command."""
    args = parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(
        level=log_level,
        json_output=args.json,
    )

    stats = PipelineStats()

    # Load configuration
    try:
        config = load_config()
        config.ensure_dirs()
    except Exception as e:
        logger.error("config_load_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)

    logger.info("pipeline_started", base_url=config.docusaurus_url)

    async def run_pipeline():
        nonlocal stats

        # Initialize components
        crawler = DocusaurusCrawler(config)
        extractor = DocusaurusContentExtractor(config.docusaurus_url)
        chunker = TextChunker(config)
        embedder = CohereEmbedder(config)
        vector_store = QdrantVectorStore(config)
        state_manager = StateManager(config)

        try:
            # ===== PHASE 1: CRAWL =====
            if not args.skip_crawl:
                stats.phases["crawl"]["started"] = datetime.utcnow().isoformat()

                logger.info("phase_crawl_started")

                # Get URLs
                urls = await crawler.fetch_sitemap()
                logger.info("sitemap_parsed", url_count=len(urls))

                # Crawl pages
                completed, failed, errors = await crawler.crawl_all(
                    urls=urls,
                    max_pages=args.max_pages,
                    resume=args.resume,
                )
                stats.phases["crawl"]["pages"] = len(completed)

                if failed:
                    stats.errors.extend([f"Crawl failed: {url} - {err}" for url, err in failed.items()])

                # Extract content
                extracted_count = 0
                for url in completed:
                    try:
                        html = await crawler.fetch_page(url)
                        doc = extractor.extract(html, url)

                        # Cache
                        url_hash = doc.get_url_hash()
                        text_content, metadata = doc.to_cache_file()
                        (config.cache_dir / "extracted" / f"{url_hash}.txt").write_text(text_content, encoding="utf-8")
                        (config.cache_dir / "extracted" / f"{url_hash}.meta.json").write_text(
                            json.dumps(metadata)
                        )
                        extracted_count += 1
                    except Exception as e:
                        stats.errors.append(f"Extraction failed: {url} - {e}")

                stats.phases["crawl"]["completed"] = datetime.utcnow().isoformat()
                logger.info(
                    "phase_crawl_complete",
                    pages_discovered=len(urls),
                    pages_crawled=len(completed),
                    pages_extracted=extracted_count,
                )
            else:
                logger.info("phase_crawl_skipped")
                stats.phases["crawl"]["completed"] = datetime.utcnow().isoformat()

            # ===== PHASE 2: EMBED =====
            if not args.skip_embed:
                stats.phases["embed"]["started"] = datetime.utcnow().isoformat()

                logger.info("phase_embed_started")

                # Load cached documents
                cache_extracted = PROJECT_ROOT / config.cache_dir / "extracted"
                documents = load_cached_documents(str(cache_extracted))
                logger.info("documents_loaded", count=len(documents))

                if documents:
                    # Chunk documents
                    all_chunks, _ = chunker.chunk_documents(documents)
                    stats.phases["embed"]["chunks"] = len(all_chunks)
                    logger.info("chunks_created", count=len(all_chunks))

                    # Generate embeddings
                    embeddings = await embedder.embed_chunks(all_chunks)
                    stats.phases["embed"]["embeddings"] = len(embeddings)

                    # Save embeddings
                    embeddings_path = "./data/embeddings.jsonl"
                    save_embeddings_to_jsonl(embeddings, embeddings_path)
                else:
                    logger.warning("no_documents_to_embed")

                stats.phases["embed"]["completed"] = datetime.utcnow().isoformat()
                logger.info("phase_embed_complete")
            else:
                logger.info("phase_embed_skipped")
                stats.phases["embed"]["completed"] = datetime.utcnow().isoformat()

            # ===== PHASE 3: UPLOAD =====
            if not args.skip_upload:
                stats.phases["upload"]["started"] = datetime.utcnow().isoformat()

                logger.info("phase_upload_started")

                # Connect to Qdrant
                connected = await vector_store.connect()
                if not connected:
                    raise ConnectionError("Failed to connect to Qdrant")

                # Create collection
                await vector_store.create_collection(recreate=args.recreate)

                # Load embeddings
                embeddings = load_embeddings_for_upload("./data/embeddings.jsonl")
                logger.info("embeddings_loaded", count=len(embeddings))

                if embeddings:
                    # Upload
                    uploaded, failed = await vector_store.upload_embeddings(embeddings)
                    stats.phases["upload"]["vectors"] = len(uploaded)

                    if failed:
                        stats.errors.extend([f"Upload failed: {id} - {err}" for id, err in failed.items()])
                else:
                    logger.warning("no_embeddings_to_upload")

                # Verify count
                final_count = await vector_store.count_vectors()

                stats.phases["upload"]["completed"] = datetime.utcnow().isoformat()
                logger.info("phase_upload_complete", total_vectors=final_count)
            else:
                logger.info("phase_upload_skipped")
                stats.phases["upload"]["completed"] = datetime.utcnow().isoformat()

            # Final summary
            stats_dict = stats.to_dict()

            if args.json:
                print(json.dumps(stats_dict))
            else:
                duration = stats_dict["duration_seconds"]
                print("\n" + "=" * 50)
                print("Pipeline Complete")
                print("=" * 50)
                print(f"  Duration: {duration:.1f} seconds")
                print()
                print("  Crawl Phase:")
                c = stats.phases["crawl"]
                print(f"    Pages discovered: {len(urls) if not args.skip_crawl else 'N/A'}")
                print(f"    Pages extracted:  {c['pages'] if not args.skip_crawl else 'N/A'}")
                print()
                print("  Embed Phase:")
                e = stats.phases["embed"]
                print(f"    Chunks created:   {e['chunks'] if not args.skip_embed else 'N/A'}")
                print(f"    Embeddings:       {e['embeddings'] if not args.skip_embed else 'N/A'}")
                print()
                print("  Upload Phase:")
                u = stats.phases["upload"]
                print(f"    Vectors uploaded: {u['vectors'] if not args.skip_upload else 'N/A'}")
                print("=" * 50)

                if stats.errors:
                    print(f"  Errors: {len(stats.errors)}")
                    for error in stats.errors[:3]:
                        print(f"    - {error}")
                    print()

            return stats_dict

        finally:
            await crawler.close()
            await embedder.close()
            await vector_store.close()

    try:
        import asyncio
        result = asyncio.run(run_pipeline())

        # Exit with error if there were failures
        if result.get("errors"):
            sys.exit(1)
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("pipeline_cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
