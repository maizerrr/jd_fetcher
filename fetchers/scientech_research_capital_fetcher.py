import requests
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class ScientechResearchCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Scientech Research Capital",
            url="https://jobs.ashbyhq.com/scientech-research?embed=js"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # Extract JSON data from script tag
            script_content = re.search(r'window\.__appData\s*=\s*({.*?});', response.text, re.DOTALL)
            if not script_content:
                raise ValueError("Could not find window.__appData in page source")

            data = json.loads(script_content.group(1))
            job_board = data.get('jobBoard', {})
            jobs_data = job_board.get('jobPostings', [])

            jobs = []
            for job in jobs_data:
                if not job.get('isListed', False):
                    continue

                jobs.append({
                    'title': job.get('title', ''),
                    'url': f"{self.url}/{job.get('id', '')}",
                    'location': job.get('locationName', 'Location not specified'),
                    'description': f"{job.get('departmentName', '')}: {job.get('title', '')}",
                    'posted_date': datetime.fromisoformat(job['publishedDate']) if job.get('publishedDate') else None
                })

            return jobs

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            return []