import requests
from typing import List, Dict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class SitemapParser:
    def __init__(self):
        pass

    def parse_sitemap(self, sitemap_url: str) -> List[Dict[str, str]]:
        """
        Parse a sitemap XML file and extract all URLs
        Returns a list of dictionaries with URL and page title
        """
        try:
            response = requests.get(sitemap_url)
            response.raise_for_status()
            
            # Parse the sitemap XML
            soup = BeautifulSoup(response.content, 'xml')
            
            urls = []
            
            # Handle regular sitemap
            for url_elem in soup.find_all('url'):
                loc_elem = url_elem.find('loc')
                if loc_elem:
                    url = loc_elem.get_text().strip()
                    # For now, we'll set title as URL until we fetch the page
                    urls.append({
                        'url': url,
                        'title': url  # Will be updated when content is fetched
                    })
            
            # Handle sitemap index (if this sitemap points to other sitemaps)
            for sitemap_elem in soup.find_all('sitemap'):
                loc_elem = sitemap_elem.find('loc')
                if loc_elem:
                    nested_sitemap_url = loc_elem.get_text().strip()
                    # Recursively parse nested sitemaps
                    nested_urls = self.parse_sitemap(nested_sitemap_url)
                    urls.extend(nested_urls)
            
            return urls
            
        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {str(e)}")
            return []

    def fetch_page_content(self, url: str) -> str:
        """
        Fetch the content of a page
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching content from {url}: {str(e)}")
            return ""

    def extract_title_from_html(self, html_content: str) -> str:
        """
        Extract the title from HTML content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            else:
                # If no title tag, try to find an h1 tag
                h1_tag = soup.find('h1')
                if h1_tag:
                    return h1_tag.get_text().strip()
                else:
                    return "Untitled Page"
        except Exception:
            return "Untitled Page"