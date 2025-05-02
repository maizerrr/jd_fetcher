import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class MillenniumFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Millennium",
            url="https://mlp.eightfold.ai/api/apply/v2/jobs/755942822827/jobs?domain=mlp.com"
        )

    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Fetches and parses job data from Eightfold API"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return [
                {
                    'title': pos.get('name', ''),
                    'description': pos.get('job_description', ''),
                    'source_site': self.site_name,
                    'url': pos.get('canonicalPositionUrl', ''),
                    'location': pos.get('location', ''),
                    'posted_date': datetime.fromtimestamp(pos['t_create']) if pos.get('t_create') else None
                }
                for pos in data.get('positions', [])
                if pos.get('name') and pos.get('canonicalPositionUrl')
            ]

        except RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Data parsing error: {str(e)}")
            return []