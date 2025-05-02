import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class TrexQuantFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="TrexQuant",
            url="https://trexquant.com/api/get-jobs"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for job in data.get('jobs', []):
                created_at_str = job.get('created_at', '').replace('Z', '+00:00')
                jobs.append({
                    'title': job.get('title', ''),
                    'description': f"{job.get('department', '')}: {job.get('title', '')}",
                    'url': job.get('url', ''),
                    'location': job.get('location', {}).get('location_str', 'Remote'),
                    'posted_date': datetime.fromisoformat(created_at_str) if created_at_str else None
                })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs