import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class RockBundFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Rock Bund Capital",
            url="https://www.rockbundcapital.com/api/jobs"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for department in data.get('departments', []):
                dept_name = department.get('name', 'Unknown Department')
                for job in department.get('jobs', []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'description': f"{dept_name}: {job.get('title', '')}",
                        'url': job.get('absolute_url', ''),
                        'location': job.get('location', {}).get('name', 'Remote'),
                        'posted_date': datetime.fromisoformat(job.get('first_published')) if job.get('first_published') else None
                    })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs