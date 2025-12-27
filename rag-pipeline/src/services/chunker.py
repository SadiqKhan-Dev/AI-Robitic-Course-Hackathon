"""Text chunking logic."""

import hashlib
import re
from typing import Optional, List, Tuple
from pathlib import Path

import structlog

from ..config import PipelineConfig
from ..models.document import DocumentPage
from ..models.chunk import TextChunk

logger = structlog.get_logger(__name__)


def count_tokens(text: str) -> int:
    """Count approximate tokens using simple word-based method."""
    # Simple approximation: 1 token ~ 4 characters
    return len(text) // 4


class TextChunker:
    """Splits text into semantically meaningful chunks."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize chunker with configuration.

        Args:
            config: Pipeline configuration (uses defaults if not provided)
        """
        self.config = config or PipelineConfig()
        self.chunk_size = self.config.chunk_size
        self.chunk_overlap = self.config.chunk_overlap

    def chunk_document(self, document: DocumentPage) -> List[TextChunk]:
        """Split a document into chunks.

        Args:
            document: DocumentPage to chunk

        Returns:
            List of TextChunk instances
        """
        text = document.extracted_text
        if not text:
            logger.warning("empty_document", url=document.url)
            return []

        # Split text into chunks
        chunks = self._split_text(text)
        if not chunks:
            return []

        # Get character positions
        char_positions = self._get_char_positions(text, chunks)

        # Count tokens for each chunk
        token_counts = [count_tokens(ct) for ct in chunks]

        # Create TextChunk instances
        text_chunks = TextChunk.from_document(
            document=document,
            chunks=chunks,
            token_counts=token_counts,
            char_positions=char_positions,
        )

        logger.debug(
            "document_chunked",
            url=document.url,
            total_chunks=len(text_chunks),
            avg_tokens=sum(token_counts) / len(token_counts) if token_counts else 0,
        )

        return text_chunks

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks respecting semantic boundaries.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = re.split(r'\n\n+', text)

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = count_tokens(para)

            # If single paragraph is too big, split by sentences
            if para_tokens > self.chunk_size * 1.5:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    sentence_tokens = count_tokens(sentence)

                    if current_tokens + sentence_tokens > self.chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        # Start new chunk with overlap
                        if self.chunk_overlap > 0 and current_chunk:
                            # Get last part for overlap
                            overlap_text = current_chunk[-self.chunk_overlap * 4:]
                            current_chunk = overlap_text
                            current_tokens = count_tokens(overlap_text)
                        else:
                            current_chunk = ""
                            current_tokens = 0

                    current_chunk += (" " if current_chunk else "") + sentence
                    current_tokens += sentence_tokens
            else:
                # Add paragraph to current chunk
                if current_tokens + para_tokens > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and current_chunk:
                        overlap_text = current_chunk[-self.chunk_overlap * 4:]
                        current_chunk = overlap_text
                        current_tokens = count_tokens(overlap_text)
                    else:
                        current_chunk = ""
                        current_tokens = 0

                current_chunk += ("\n\n" if current_chunk else "") + para
                current_tokens += para_tokens

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:self.chunk_size * 4]]

    def _get_char_positions(
        self, full_text: str, chunks: List[str]
    ) -> List[Tuple[int, int]]:
        """Find character positions for each chunk in the original text.

        Args:
            full_text: Original text
            chunks: List of chunk texts

        Returns:
            List of (start, end) positions
        """
        positions = []
        current_pos = 0

        for chunk in chunks:
            # Find chunk in text starting from current position
            start = full_text.find(chunk, current_pos)
            if start == -1:
                # Fallback to approximate position
                start = current_pos
                end = start + len(chunk)
            else:
                end = start + len(chunk)

            positions.append((start, end))
            current_pos = end - (self.chunk_overlap * 4 if self.chunk_overlap > 0 else 0)

        return positions

    def chunk_documents(
        self, documents: List[DocumentPage]
    ) -> Tuple[List[TextChunk], dict[str, int]]:
        """Split multiple documents into chunks.

        Args:
            documents: List of DocumentPages to chunk

        Returns:
            Tuple of (all_chunks, chunk_counts_by_url)
        """
        all_chunks = []
        chunk_counts = {}

        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
            chunk_counts[doc.url] = len(chunks)

        logger.info(
            "documents_chunked",
            total_documents=len(documents),
            total_chunks=len(all_chunks),
        )

        return all_chunks, chunk_counts

    def chunk_text(self, text: str, source_url: str = "", source_title: str = "") -> List[TextChunk]:
        """Split raw text into chunks without a DocumentPage.

        Args:
            text: Text to chunk
            source_url: Source URL for metadata
            source_title: Source title for metadata

        Returns:
            List of TextChunk instances
        """
        if not text:
            return []

        # Split text
        chunks = self._split_text(text)
        if not chunks:
            return []

        # Count tokens
        token_counts = [count_tokens(ct) for ct in chunks]

        # Create minimal chunks
        url_hash = hashlib.md5(source_url.encode()).hexdigest()[:16] if source_url else "text"
        return [
            TextChunk(
                chunk_id=f"{url_hash}_{i}",
                text=chunk_text,
                source_url=source_url,
                source_title=source_title,
                chunk_index=i,
                total_chunks=len(chunks),
                token_count=token_counts[i],
                char_start=0,
                char_end=len(chunk_text),
                metadata={},
            )
            for i, chunk_text in enumerate(chunks)
        ]
