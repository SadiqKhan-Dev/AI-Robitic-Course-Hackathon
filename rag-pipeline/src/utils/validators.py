"""Input validation utilities."""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate a URL string.

    Args:
        url: URL string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        result = urlparse(url)
        if not result.scheme:
            return False, "URL must start with http:// or https://"
        if not result.netloc:
            return False, "URL must have a valid domain"
        return True, None
    except Exception as e:
        return False, f"Invalid URL format: {e}"


def is_valid_url(url: str) -> bool:
    """Quick check if URL is valid (returns bool only)."""
    is_valid, _ = validate_url(url)
    return is_valid


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text content.

    Args:
        text: Text to sanitize
        max_length: Optional maximum length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes and other control characters
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize whitespace (collapse multiple spaces, trim)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL string
    """
    url = url.strip()
    # Remove trailing slashes (except for root)
    if len(url) > 1 and url.endswith("/"):
        url = url[:-1]
    return url


def extract_url_hash(url: str) -> str:
    """Generate a short hash for a URL for use as filename.

    Args:
        url: URL to hash

    Returns:
        Short hex hash string
    """
    import hashlib

    # Normalize URL first
    normalized = normalize_url(url)
    # Create short hash
    return hashlib.md5(normalized.encode()).hexdigest()[:16]
