import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class BridgewaterFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Bridgewater",
            url="https://www.bridgewater.com/jobboard"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        jobs = []

        for department in data.get('departments', []):
            if department['name'] == 'All Departments':
                continue

            for job in department.get('jobs', []):
                jobs.append({
                    'title': job['title'],
                    'url': job['absolute_url'],
                    'location': job['location']['name'],
                    'posted_date': datetime.fromisoformat(job['first_published']),
                    'description': f"Department: {department['name']}\n"
                                  f"Role ID: {job['requisition_id']}"
                })

        return jobs