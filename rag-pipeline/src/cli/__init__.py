"""CLI module imports."""

from .crawl import main as crawl_main
from .embed import main as embed_main
from .upload import main as upload_main
from .pipeline import main as pipeline_main

__all__ = [
    "crawl_main",
    "embed_main",
    "upload_main",
    "pipeline_main",
]
