import requests
import logging
import re
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class FlowTraderFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Flow Traders",
            url="https://boards-api.greenhouse.io/v1/boards/flowtraders/jobs?content=true&per_page=500"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for job in data.get('jobs', []):
                # Clean HTML entities from content using BeautifulSoup
                description = BeautifulSoup(job.get('content', ''), 'html.parser').get_text(separator='\n')
                description = re.sub(r'<[^>]+>', '', description)
                
                # Extract department names
                departments = [dept['name'] for dept in job.get('departments', [])]
                
                jobs.append({
                    'title': job.get('title', ''),
                    'description': f"Departments: {', '.join(departments)}\n\n{description}",
                    'url': job.get('absolute_url', ''),
                    'location': job.get('location', {}).get('name', 'Remote'),
                    'posted_date': datetime.fromisoformat(job.get('first_published', '')) if job.get('first_published') else None
                })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs