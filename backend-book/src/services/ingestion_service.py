from typing import List, Dict
from src.services.qdrant_service import QdrantService
from src.services.embedding_service import EmbeddingService
from src.utils.text_chunker import TextChunker
from src.utils.sitemap_parser import SitemapParser
from src.models.book_content import BookContent
import logging


class IngestionService:
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        self.text_chunker = TextChunker()
        self.sitemap_parser = SitemapParser()
        self.logger = logging.getLogger(__name__)

    def ingest_from_sitemap(self, sitemap_url: str) -> Dict[str, any]:
        """
        Main method to ingest book content from a sitemap
        """
        try:
            # 1. Parse the sitemap to get all URLs
            self.logger.info(f"Starting ingestion from sitemap: {sitemap_url}")
            urls = self.sitemap_parser.parse_sitemap(sitemap_url)
            self.logger.info(f"Found {len(urls)} URLs in sitemap")

            # 2. Fetch content for each URL and extract titles
            all_chunks = []
            for i, url_info in enumerate(urls):
                self.logger.info(f"Processing {i+1}/{len(urls)}: {url_info['url']}")
                
                # Fetch content
                content = self.sitemap_parser.fetch_page_content(url_info['url'])
                if not content:
                    self.logger.warning(f"Could not fetch content for {url_info['url']}")
                    continue
                
                # Extract title
                title = self.sitemap_parser.extract_title_from_html(content)
                url_info['title'] = title
                
                # Chunk the content
                chunks = self.text_chunker.chunk_html_content(
                    content, 
                    url_info['url'], 
                    url_info['title']
                )
                
                all_chunks.extend(chunks)
                self.logger.info(f"Created {len(chunks)} chunks for {url_info['url']}")

            # 3. Generate embeddings for all chunks
            self.logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
            texts_to_embed = [chunk['content'] for chunk in all_chunks]
            embeddings = self.embedding_service.create_embeddings_batch(texts_to_embed)
            
            # 4. Add embeddings to chunks
            for i, chunk in enumerate(all_chunks):
                chunk['embedding'] = embeddings[i]
            
            # 5. Store in Qdrant
            self.logger.info("Storing embeddings in Qdrant")
            self.qdrant_service.store_embeddings(all_chunks)
            
            result = {
                "status": "success",
                "total_pages": len(urls),
                "total_chunks": len(all_chunks),
                "message": f"Successfully ingested {len(all_chunks)} content chunks from {len(urls)} pages"
            }
            
            self.logger.info(result["message"])
            return result
            
        except Exception as e:
            self.logger.error(f"Error during ingestion: {str(e)}")
            return {
                "status": "error",
                "message": f"Ingestion failed: {str(e)}"
            }

    def get_ingested_content_stats(self) -> Dict[str, any]:
        """
        Get statistics about the ingested content
        """
        try:
            all_docs = self.qdrant_service.get_all_documents()
            urls = set(doc['url'] for doc in all_docs)
            
            stats = {
                "total_documents": len(all_docs),
                "unique_pages": len(urls),
                "pages": list(urls)
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting content stats: {str(e)}")
            return {
                "status": "error",
                "message": f"Could not retrieve stats: {str(e)}"
            }