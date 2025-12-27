"""Web crawler for Docusaurus sites."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from lxml import etree
from pydantic import BaseModel, Field

import structlog

from ..config import PipelineConfig
from ..utils.retry import retry_with_exponential_backoff

logger = structlog.get_logger(__name__)

def _strip_namespaces(tree):
    """Remove namespace prefixes from all elements in an XML tree."""
    for elem in tree.getiterator():
        if elem.tag.startswith("{"):
            elem.tag = elem.tag.split("}", 1)[1]


class CrawlState(BaseModel):
    """Tracks crawling progress for resumability."""

    urls_discovered: list[str] = Field(default_factory=list)
    urls_completed: list[str] = Field(default_factory=list)
    urls_failed: dict[str, str] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    total_pages: int = 0
    completed_pages: int = 0

    def is_completed(self, url: str) -> bool:
        """Check if URL has been crawled."""
        return url in self.urls_completed

    def mark_completed(self, url: str):
        """Mark URL as completed."""
        if url not in self.urls_completed:
            self.urls_completed.append(url)
            self.completed_pages += 1
            self.last_updated = datetime.utcnow()

    def mark_failed(self, url: str, error: str):
        """Mark URL as failed with error message."""
        self.urls_failed[url] = error
        self.last_updated = datetime.utcnow()

    def get_pending_urls(self) -> list[str]:
        """Get URLs that need to be crawled."""
        completed_set = set(self.urls_completed)
        failed_set = set(self.urls_failed.keys())
        return [
            url for url in self.urls_discovered
            if url not in completed_set and url not in failed_set
        ]

    def to_json(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "urls_discovered": self.urls_discovered,
            "urls_completed": self.urls_completed,
            "urls_failed": self.urls_failed,
            "last_updated": self.last_updated.isoformat(),
            "total_pages": self.total_pages,
            "completed_pages": self.completed_pages,
        }

    @classmethod
    def from_json(cls, data: dict) -> "CrawlState":
        """Create from JSON data."""
        return cls(
            urls_discovered=data.get("urls_discovered", []),
            urls_completed=data.get("urls_completed", []),
            urls_failed=data.get("urls_failed", {}),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.utcnow().isoformat())),
            total_pages=data.get("total_pages", 0),
            completed_pages=data.get("completed_pages", 0),
        )


class DocusaurusCrawler:
    """Crawls Docusaurus documentation sites."""

    def __init__(self, config: PipelineConfig):
        """Initialize crawler with configuration.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.state = CrawlState()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "RAG-Pipeline/0.1 (+https://github.com/ai-robotic-course)",
                },
            )
        return self.session

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_sitemap(self) -> list[str]:
        """Fetch and parse sitemap.xml to discover all URLs.

        Returns:
            List of discovered URLs
        """
        session = await self._get_session()

        async def _fetch():
            response = await session.get(self.config.sitemap_url)
            response.raise_for_status()
            return await response.text()

        try:
            sitemap_xml = await retry_with_exponential_backoff(
                _fetch,
                max_retries=3,
                base_delay=2.0,
                exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
            )

            # Parse XML
            parser = etree.XMLParser(remove_comments=True)
            tree = etree.fromstring(sitemap_xml.encode(), parser)
            _strip_namespaces(tree)

            # Extract URLs from sitemap
            urls = []
            base_url = self.config.docusaurus_url.rstrip("/")

            # Handle sitemap index (multiple sitemaps)
            for sitemap in tree.findall("sitemap"):
                loc = sitemap.find("loc")
                if loc is not None and loc.text and "sitemap.xml" not in loc.text:
                    nested_urls = await self._fetch_nested_sitemap(loc.text, session)
                    urls.extend(nested_urls)

            # Handle URL entries
            for url_elem in tree.findall("url"):
                loc = url_elem.find("loc")
                if loc is not None and loc.text:
                    # Filter to docs pages only
                    if "/docs/" in loc.text or loc.text.endswith("/docs"):
                        urls.append(loc.text)

            logger.info("sitemap_parsed", url_count=len(urls))
            return urls

        except Exception as e:
            logger.error("sitemap_fetch_failed", error=str(e))
            raise

    async def _fetch_nested_sitemap(self, sitemap_url: str, session: aiohttp.ClientSession) -> list[str]:
        """Fetch a nested sitemap and extract URLs.

        Args:
            sitemap_url: URL of the nested sitemap
            session: HTTP session

        Returns:
            List of URLs from nested sitemap
        """
        try:
            async def _fetch():
                response = await session.get(sitemap_url)
                response.raise_for_status()
                return await response.text()

            sitemap_xml = await retry_with_exponential_backoff(
                _fetch,
                max_retries=2,
                base_delay=1.0,
                exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
            )

            parser = etree.XMLParser(remove_comments=True)
            tree = etree.fromstring(sitemap_xml.encode(), parser)
            _strip_namespaces(tree)

            urls = []
            for url_elem in tree.xpath("//*[local-name() = 'url']"):
                loc = url_elem.find(".//*[local-name() = 'loc']")
                if loc is not None and loc.text:
                    urls.append(loc.text)

            return urls

        except Exception as e:
            logger.warning("nested_sitemap_failed", url=sitemap_url, error=str(e))
            return []

    async def fetch_page(self, url: str) -> str:
        """Fetch a single page.

        Args:
            url: URL to fetch

        Returns:
            HTML content
        """
        session = await self._get_session()

        async def _fetch():
            response = await session.get(url, allow_redirects=True)
            response.raise_for_status()
            return await response.text()

        return await retry_with_exponential_backoff(
            _fetch,
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
        )

    async def crawl_all(
        self,
        urls: Optional[list[str]] = None,
        max_pages: Optional[int] = None,
        resume: bool = False,
    ) -> tuple[list[str], list[str], dict[str, str]]:
        """Crawl all URLs.

        Args:
            urls: Optional list of URLs to crawl (uses sitemap if not provided)
            max_pages: Maximum number of pages to crawl
            resume: Whether to resume from previous state

        Returns:
            Tuple of (completed_urls, failed_urls, errors)
        """
        if urls is None:
            urls = await self.fetch_sitemap()

        # Load state if resuming
        if resume:
            state_path = self.config.get_state_path("crawl")
            if state_path.exists():
                self.state = CrawlState.from_json(json.loads(state_path.read_text()))
                logger.info("state_loaded", completed=self.state.completed_pages)

        # Filter to URLs that need crawling
        pending_urls = [url for url in urls if not self.state.is_completed(url)]

        if max_pages:
            pending_urls = pending_urls[:max_pages]

        self.state.urls_discovered = urls
        self.state.total_pages = len(urls)

        # Rate limiting
        delay = self.config.request_delay
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

        async def crawl_with_semaphore(url: str) -> tuple[str, Optional[str]]:
            async with semaphore:
                await asyncio.sleep(delay)  # Rate limit
                try:
                    await self.fetch_page(url)
                    self.state.mark_completed(url)
                    return url, None
                except Exception as e:
                    error_msg = str(e)
                    self.state.mark_failed(url, error_msg)
                    return None, error_msg

        # Crawl all pages
        results = await asyncio.gather(
            *[crawl_with_semaphore(url) for url in pending_urls],
            return_exceptions=True,
        )

        # Save state
        state_path = self.config.get_state_path("crawl")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(self.state.to_json()))

        # Separate results
        completed = []
        failed = {}
        for result in results:
            if isinstance(result, Exception):
                failed["unknown"] = str(result)
            elif result[0] is not None:
                completed.append(result[0])
            else:
                failed[result[1]] = result[1]

        logger.info(
            "crawl_complete",
            total=len(urls),
            completed=len(completed),
            failed=len(failed),
        )

        return completed, failed, self.state.urls_failed
