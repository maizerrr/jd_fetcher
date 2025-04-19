import requests
import logging
from typing import List, Dict, Any
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class BaseFetcher:
    def __init__(self, site_name, url):
        self.site_name = site_name
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 30  # Default timeout in seconds
        self.max_retries = 3
    
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        """
        Fetches job listings from the site and returns parsed job data.
        Returns list of job dicts or raises exception.
        """
        html = self._get_html()
        return self.parse_jobs(html)
    
    def _get_html(self) -> str:
        """
        Makes HTTP GET request to the job site with retries.
        Returns HTML content as string or raises exception.
        """
        retry_count = 0
        last_exception = None
        
        while retry_count < self.max_retries:
            try:
                logger.info(f"Fetching jobs from {self.site_name} at {self.url}")
                response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                return response.text
            except RequestException as e:
                retry_count += 1
                last_exception = e
                logger.warning(f"Attempt {retry_count} failed for {self.site_name}: {str(e)}")
        
        # If we've exhausted retries, log and re-raise the last exception
        logger.error(f"Failed to fetch jobs from {self.site_name} after {self.max_retries} attempts")
        raise last_exception or RequestException(f"Failed to fetch jobs from {self.site_name}")
    
    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """
        Parses HTML content to extract job listings.
        To be implemented by subclasses (site-specific parsing).
        """
        raise NotImplementedError("Subclasses must implement parse_jobs method")