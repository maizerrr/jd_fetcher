import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class PanAgoraFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="PanAgora Asset Management",
            url="https://empower.wd12.myworkdayjobs.com/wday/cxs/empower/PanAgora/jobs"
        )
        self.headers.update({
            'Origin': 'https://empower.wd12.myworkdayjobs.com',
            'Referer': 'https://empower.wd12.myworkdayjobs.com/PanAgora'
        })

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        limit = 20
        offset = 0
        total = None

        try:
            while total is None or offset < total:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json={
                        "appliedFacets": {},
                        "limit": limit,
                        "offset": offset,
                        "searchText": ""
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                if total is None:
                    total = data.get('total', 0)

                for job in data.get('jobPostings', []):
                    try:
                        posted_date = self._parse_posted_date(job.get('postedOn'))
                        jobs.append({
                            'title': job.get('title', ''),
                            'description': f"{job.get('title', '')} - {job.get('locationsText', '')}",
                            'url': f"https://empower.wd12.myworkdayjobs.com/en-US/PanAgora{job.get('externalPath', '')}",
                            'location': job.get('locationsText', ''),
                            'posted_date': posted_date
                        })
                    except Exception as e:
                        logger.warning(f"Error processing job: {str(e)}")

                offset += limit

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")

        return jobs

    def _parse_posted_date(self, posted_str: str) -> datetime:
        if not posted_str:
            return None
        try:
            days_ago = int(posted_str.lower().replace('posted', '').replace('days ago', '').strip())
            return datetime.now() - timedelta(days=days_ago)
        except ValueError:
            logger.warning(f"Could not parse date string: {posted_str}")
            return None