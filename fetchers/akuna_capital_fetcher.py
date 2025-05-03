import requests
import logging
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class AkunaCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Akuna Capital",
            url="https://akunacapital.com/wp-admin/admin-ajax.php?action=gh_ajax_request&experience=&department=&location=&search_term="
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return [
                {
                    'title': job.get('name', ''),
                    'description': f"Departments: {', '.join(job.get('department', []))}\nSpecialties: {', '.join(job.get('specialties', []))}",
                    'url': f"https://akunacapital.com/job-details?gh_jid={job.get('id', '')}",
                    'location': job.get('location', [''])[0],
                    'posted_date': None
                }
                for job in data.get('matched_jobs', [])
                if job.get('id')
            ]

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            return []