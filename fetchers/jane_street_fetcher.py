import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class JaneStreetFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Jane Street",
            url="https://www.janestreet.com/jobs/main.json"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            jobs_data = response.json()

            return [
                {
                    'title': job.get('position', ''),
                    'description': BeautifulSoup(job.get('overview', ''), 'html.parser').get_text(),
                    'url': f"https://www.janestreet.com/join-jane-street/position/{job.get('id', '')}",
                    'location': job.get('city', ''),
                    'posted_date': None  # API doesn't provide posting dates
                }
                for job in jobs_data
                if job.get('position') and job.get('id')
            ]

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            return []