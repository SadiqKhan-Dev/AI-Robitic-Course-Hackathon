"""Crawl CLI command for content ingestion."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from ..config import load_config
from ..services.crawler import DocusaurusCrawler
from ..services.extractor import DocusaurusContentExtractor
from ..services.state_manager import StateManager
from ..utils.logger import setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Crawl Docusaurus documentation site and extract content"
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
        help="Resume from previous crawl state",
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
        "--urls",
        type=str,
        default=None,
        help="Comma-separated list of URLs to crawl (overrides sitemap)",
    )
    return parser.parse_args()


def main():
    """Main entry point for crawl command."""
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

    logger.info("crawl_started", base_url=config.docusaurus_url)

    # Parse URLs if provided (use None for sitemap discovery)
    provided_urls = None
    if args.urls:
        provided_urls = [u.strip() for u in args.urls.split(",")]

    # Initialize components
    crawler = DocusaurusCrawler(config)
    extractor = DocusaurusContentExtractor(config.docusaurus_url)
    state_manager = StateManager(config)

    async def run_crawl():
        # Get URLs to crawl
        urls_to_crawl = provided_urls
        if urls_to_crawl is None:
            logger.info("fetching_sitemap", sitemap_url=config.sitemap_url)
            urls_to_crawl = await crawler.fetch_sitemap()
            logger.info("sitemap_parsed", url_count=len(urls_to_crawl))

        # Crawl pages
        completed, failed, errors = await crawler.crawl_all(
            urls=urls_to_crawl,
            max_pages=args.max_pages,
            resume=args.resume,
        )

        # Extract content from crawled pages
        state = state_manager.get_crawl_state()
        pending_urls = state.get_pending_urls()

        extracted = {}
        failed_extraction = {}

        for url in completed:
            try:
                html = await crawler.fetch_page(url)
                doc = extractor.extract(html, url)

                # Cache the extracted content
                url_hash = doc.get_url_hash()
                text_path = config.get_cache_path(url_hash, "txt")
                meta_path = config.get_cache_path(url_hash, "meta.json")

                text_content, metadata = doc.to_cache_file()
                text_path.write_text(text_content, encoding="utf-8")
                meta_path.write_text(json.dumps(metadata))

                extracted[url] = doc
                logger.debug("extracted", url=url, text_length=len(doc.extracted_text))

            except Exception as e:
                logger.error("extraction_failed", url=url, error=str(e))
                failed_extraction[url] = str(e)

        # Save final state
        state_manager.save_state("crawl")

        return {
            "urls_discovered": len(urls_to_crawl),
            "urls_completed": len(completed),
            "urls_failed": len(failed),
            "pages_extracted": len(extracted),
            "extraction_failed": len(failed_extraction),
        }

    try:
        result = asyncio.run(run_crawl())

        if args.json:
            print(json.dumps(result))
        else:
            print("\n" + "=" * 50)
            print("Crawl Complete")
            print("=" * 50)
            print(f"  Discovered: {result['urls_discovered']} URLs")
            print(f"  Crawled:    {result['urls_completed']} pages")
            print(f"  Failed:     {result['urls_failed']} URLs")
            print(f"  Extracted:  {result['pages_extracted']} pages")
            print(f"  Extraction failed: {result['extraction_failed']} pages")
            print("=" * 50)

        sys.exit(0 if result["urls_failed"] == 0 and result["extraction_failed"] == 0 else 1)

    except KeyboardInterrupt:
        logger.info("crawl_cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("crawl_failed", error=str(e))
        if args.json:
            print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        asyncio.run(DocusaurusCrawler(config).close())


if __name__ == "__main__":
    main()
