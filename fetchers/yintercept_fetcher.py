import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher
import logging

logger = logging.getLogger(__name__)

class YInterceptFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Y-Intercept",
            url="https://y-intercept.org/careers/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        html = self._get_html()
        return self.parse_jobs(html)

    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='post-content')
        
        if not container:
            raise ValueError("Could not find post-content container")

        jobs = []
        for heading in container.find_all('h2'):
            link = heading.find('a')
            if not link:
                continue

            jobs.append({
                'title': link.text.strip(),
                'url': f"https://y-intercept.org{link['href']}",
                'location': 'Hong Kong',
                'posted_date': datetime.utcnow(),
                'description': ''  # Description not available in example
            })

        return jobs