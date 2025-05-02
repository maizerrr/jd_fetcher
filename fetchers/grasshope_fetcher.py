import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher
import logging

logger = logging.getLogger(__name__)

class GrasshopeFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Grasshope",
            url="https://grasshopperasia.com/job/trading/"
        )
    
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs = []
            job_list = soup.find('ul', class_='job_list')
            if job_list:
                for item in job_list.find_all('li'):
                    link = item.find('a')
                    if link:
                        jobs.append({
                            'title': link.text.strip(),
                            'url': link['href'],
                            'location': 'Singapore',  # Hardcoded as requested
                            'posted_date': None,  # Set to unknown
                            'description': link.text.strip()  # Same as title
                        })
            return jobs
        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            return []