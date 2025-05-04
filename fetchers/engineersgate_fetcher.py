import requests
import logging
import html
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class EngineersGateFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Engineers Gate",
            url="https://boards-api.greenhouse.io/v1/boards/engineersgate/jobs?gh_src=6be3e724&content=true"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for job in data.get('jobs', []):
                try:
                    description = BeautifulSoup(html.unescape(job.get('content', '')), 'html.parser').get_text(separator=' ', strip=True) if job.get('content') else ''
                    jobs.append({
                        'title': job.get('title', ''),
                        'url': job.get('absolute_url', ''),
                        'location': job.get('location', {}).get('name', ''),
                        'description': description,
                        'posted_date': datetime.fromisoformat(job['first_published']) if job.get('first_published') else None
                    })
                except Exception as e:
                    logger.warning(f"Error processing job {job.get('id')}: {str(e)}")

            logger.info(f"Fetched {len(jobs)} jobs from {self.site_name}")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            return []