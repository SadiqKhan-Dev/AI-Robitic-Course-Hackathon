import re
from typing import List, Dict
from config.settings import settings


class TextChunker:
    def __init__(self, chunk_size: int = 512, overlap: float = 0.2):
        """
        Initialize the text chunker with specified chunk size and overlap
        :param chunk_size: Target size for each chunk in tokens (approximate)
        :param overlap: Overlap percentage between chunks (0.0 to 1.0)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Rough estimation: 1 token ~ 4 characters for English text
        self.chars_per_chunk = int(chunk_size * 4)
        self.overlap_chars = int(self.chars_per_chunk * overlap)

    def chunk_text(self, text: str, url: str, title: str) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata
        """
        if not text.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # Determine the end position
            end = start + self.chars_per_chunk
            
            # If we're near the end, adjust to include the remainder
            if end >= len(text):
                end = len(text)
            else:
                # Try to break at sentence boundary
                temp_end = end
                while temp_end < len(text) and text[temp_end] not in '.!?。！？\n':
                    temp_end += 1
                
                # If no sentence boundary found, break at word boundary
                if temp_end >= len(text) or text[temp_end] not in '.!?。！？\n':
                    temp_end = end
                    while temp_end < len(text) and text[temp_end] != ' ':
                        temp_end += 1
                
                # If still no good break point, just break at the original end
                if temp_end > end:
                    temp_end = end
                
                end = temp_end + 1  # Include the punctuation/space

            # Extract the chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    'id': f"{url}#{chunk_index}",
                    'content': chunk_text,
                    'url': url,
                    'title': title,
                    'chunk_index': chunk_index,
                    'metadata': {}
                })
            
            # Move start position, accounting for overlap
            start = end - self.overlap_chars
            if start < end:  # Ensure we're making progress
                chunk_index += 1
            else:
                # If overlap would cause infinite loop, advance by one character
                start = end
                chunk_index += 1

        return chunks

    def chunk_html_content(self, html_content: str, url: str, title: str) -> List[Dict]:
        """
        Extract text from HTML and chunk it
        """
        # Simple HTML tag removal - in a real implementation, you'd want to use
        # a proper HTML parser like BeautifulSoup
        clean_text = re.sub(r'<[^>]+>', ' ', html_content)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return self.chunk_text(clean_text, url, title)