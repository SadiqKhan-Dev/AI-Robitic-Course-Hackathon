"""HTML content extraction for Docusaurus pages."""

import re
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

import structlog

from ..models.document import DocumentPage

logger = structlog.get_logger(__name__)


class DocusaurusContentExtractor:
    """Extracts main content from Docusaurus HTML pages."""

    # Selectors for main content area in Docusaurus
    CONTENT_SELECTORS = [
        "article",
        '[role="main"]',
        ".main-content",
        "#__docusaurus",
        "main",
    ]

    # Elements to remove (navigation, footer, etc.)
    REMOVE_SELECTORS = [
        "nav",
        "header",
        "footer",
        ".navbar",
        ".footer",
        ".theme-code-block-highlighted-line",
        ".code-block-content",
        ".pagination-nav",
        ".table-of-contents",
        ".breadcrumbs",
        ".menu__link--sublist",
        ".theme-doc-sidebar-container",
        ".theme-doc-toc-mobile",
        ".theme-last-updated",
        ".theme-edit-this-page",
        "[role=navigation]",
        ".admonition",
    ]

    def __init__(self, base_url: str):
        """Initialize extractor with base URL.

        Args:
            base_url: Base URL of the Docusaurus site
        """
        self.base_url = base_url.rstrip("/")

    def extract(self, html: str, url: str) -> DocumentPage:
        """Extract main content from HTML.

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            DocumentPage with extracted content
        """
        soup = BeautifulSoup(html, "lxml")

        # Extract title
        title = self._extract_title(soup)

        # Extract main content
        content_element = self._find_content_element(soup)

        if content_element is None:
            logger.warning("no_content_found", url=url)
            # Fallback to body
            content_element = soup.find("body")
            if content_element is None:
                raise ValueError(f"Could not find content in {url}")

        # Clean content
        self._clean_content(content_element)

        # Get text content
        text = self._extract_text(content_element)

        # Normalize text
        text = self._normalize_text(text)

        logger.debug("content_extracted", url=url, title=title, text_length=len(text))

        return DocumentPage(
            url=url,
            title=title,
            extracted_text=text,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title.

        Args:
            soup: BeautifulSoup object

        Returns:
            Page title string
        """
        # Try h1 first (Docusaurus uses h1 for page titles)
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
            if title:
                return title

        # Fallback to title tag
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove site suffix (e.g., " | Docusaurus")
            if " | " in title:
                title = title.split(" | ")[0]
            return title

        return "Untitled"

    def _find_content_element(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main content element.

        Args:
            soup: BeautifulSoup object

        Returns:
            Content element or None
        """
        for selector in self.CONTENT_SELECTORS:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element
        return None

    def _clean_content(self, element: Tag):
        """Remove non-content elements from content area.

        Args:
            element: Content element to clean
        """
        # Remove unwanted elements
        for selector in self.REMOVE_SELECTORS:
            for el in element.select(selector):
                el.decompose()

        # Remove empty elements
        for el in element.find_all():
            # Skip if it's a code block (keep the code)
            if el.name == "code":
                continue

            # Remove if empty or only whitespace
            text = el.get_text(strip=True)
            if not text and not el.find_all(recursive=False):
                el.decompose()

    def _extract_text(self, element: Tag) -> str:
        """Extract clean text from element.

        Args:
            element: HTML element

        Returns:
            Clean text content
        """
        # Get text with newline separators
        text = element.get_text(separator="\n", strip=True)

        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _normalize_text(self, text: str) -> str:
        """Normalize text content.

        Args:
            text: Raw text

        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n[ \t]+", "\n", text)

        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip leading/trailing whitespace
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(line for line in lines if line)

        return text.strip()

    def extract_batch(self, html_pages: dict[str, str]) -> dict[str, DocumentPage]:
        """Extract content from multiple pages.

        Args:
            html_pages: Dict of URL -> HTML content

        Returns:
            Dict of URL -> DocumentPage
        """
        results = {}
        for url, html in html_pages.items():
            try:
                doc = self.extract(html, url)
                results[url] = doc
            except Exception as e:
                logger.error("extraction_failed", url=url, error=str(e))
                raise

        logger.info("batch_extracted", count=len(results))
        return results
