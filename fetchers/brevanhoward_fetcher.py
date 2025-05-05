import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class BrevanHowardFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Brevan Howard",
            url="https://wd3.myworkdaysite.com/wday/cxs/brevanhoward/BH_ExternalCareers/jobs"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        # Get fresh CSRF token and session cookie
        session = requests.Session()
        init_response = session.get(
            'https://wd3.myworkdaysite.com/recruiting/brevanhoward/BH_ExternalCareers',
            headers={
                **self.headers,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cache-Control': 'no-cache'
            },
            timeout=self.timeout
        )
        if not init_response.cookies.get('CALYPSO_CSRF_TOKEN'):
            raise ValueError("CSRF token cookie not received in initial response")
        init_response.raise_for_status()

        # Extract CSRF token from response headers
        csrf_token = session.cookies.get('CALYPSO_CSRF_TOKEN')
        if not csrf_token:
            raise ValueError("CSRF token not found in initial response")

        headers = {
            **self.headers,
            'accept': 'application/json',
            'accept-language': 'en-US',
            'origin': 'https://wd3.myworkdaysite.com',
            'referer': 'https://wd3.myworkdaysite.com/recruiting/brevanhoward/BH_ExternalCareers',
            'x-calypso-csrf-token': csrf_token,
            'Content-Type': 'application/json'
        }

        all_jobs = []
        offset = 0
        total = None

        while True:
            response = session.post(
                self.url,
                headers=headers,
                json={
                    "appliedFacets": {},
                    "limit": 20,
                    "offset": offset,
                    "searchText": ""
                },
                timeout=self.timeout
            )
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                raise RuntimeError(
                    f"API request failed: {e.response.status_code} {e.response.reason}\n"
                    f"Response body: {e.response.text[:500]}"
                ) from e
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise ValueError("Invalid JSON response from API") from e

            if total is None:
                total = data.get('total', 0)
            all_jobs.extend(data.get('jobPostings', []))
            
            if offset >= total:
                break
            offset += 20

        return [
            {
                'title': job.get('title', ''),
                'description': ', '.join(job.get('bulletFields', [])),
                'url': f"https://wd3.myworkdaysite.com/en-US/recruiting/brevanhoward/BH_ExternalCareers{job.get('externalPath', '')}",
                'location': job.get('locationsText', 'Remote'),
                'posted_date': self.parse_relative_date(job.get('postedOn', ''))
            }
            for job in all_jobs
        ]

    def parse_relative_date(self, date_str: str) -> datetime:
        try:
            days_ago = int(date_str.split()[1])
            return datetime.utcnow() - timedelta(days=days_ago)
        except (IndexError, ValueError):
            logger.warning(f"Could not parse date string: {date_str}")
            return datetime.utcnow()