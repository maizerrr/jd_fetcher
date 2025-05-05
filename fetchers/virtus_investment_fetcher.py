import requests
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class VirtusInvestmentPartnersFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Virtus Investment Partners",
            url="https://virtus.wd5.myworkdayjobs.com/wday/cxs/virtus/VirtusCareers/jobs"
        )
        self.base_url = "https://virtus.wd5.myworkdayjobs.com/en-US/VirtusCareers"
        self.session = requests.Session()


    def _parse_relative_date(self, date_str: str) -> datetime:
        try:
            match = re.search(r'(\d+)\s+(day|week|month)', date_str, re.IGNORECASE)
            if not match:
                return datetime.utcnow()

            num = int(match.group(1))
            unit = match.group(2).lower()
            if unit == 'day':
                delta = timedelta(days=num)
            elif unit == 'week':
                delta = timedelta(weeks=num)
            elif unit == 'month':
                delta = timedelta(days=30*num)
            return datetime.utcnow() - delta
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}': {str(e)}")
            return datetime.utcnow()

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []

        # Initial request to establish session and get CSRF token
        init_response = self.session.get(
            'https://virtus.wd5.myworkdayjobs.com/VirtusCareers',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cache-Control': 'no-cache'
            }
        )
        init_response.raise_for_status()

        if not init_response.cookies.get('CALYPSO_CSRF_TOKEN'):
            raise Exception("CSRF token cookie not received in initial response")

        csrf_token = init_response.cookies['CALYPSO_CSRF_TOKEN']
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US',
            'origin': 'https://virtus.wd5.myworkdayjobs.com',
            'referer': init_response.url,
            'x-calypso-csrf-token': csrf_token,
            'Content-Type': 'application/json'
        }

        limit = 20
        offset = 0
        total = None

        try:
            while total is None or offset < total:
                response = self.session.post(
                    self.url,
                    headers=headers,
                    json={
                        "appliedFacets": {},
                        "limit": 20,
                        "offset": offset,
                        "searchText": ""
                    }
                )
                logger.debug(f"API Request: {response.request.method} {response.request.url}")
                logger.debug(f"Request Headers: {dict(response.request.headers)}")
                
                try:
                    response.raise_for_status()
                    data = response.json()
                    logger.debug(f"API Response: {data.get('total', 0)} total jobs")
                except Exception as e:
                    logger.error(f"API request failed: {str(e)}")
                    logger.debug(f"Response status: {response.status_code}")
                    logger.debug(f"Response content: {response.text[:500]}")
                    break

                page_jobs = data.get('jobPostings', [])
                total = data.get('total', 0)
                logger.info(f"Page {offset//20 + 1}: Found {len(page_jobs)} jobs")
                if len(page_jobs) == 0:
                    logger.warning("Empty page received - possible API pagination issue")

                for posting in data.get('jobPostings', []):
                    logger.debug(f"Processing job: {posting.get('title', '')}")
                    jobs.append({
                        'title': posting.get('title', ''),
                        'description': ", ".join(posting.get('bulletFields', [])),
                        'url': f"{self.base_url}{posting.get('externalPath', '')}",
                        'location': posting.get('locationsText', ''),
                        'posted_date': self._parse_relative_date(posting.get('postedOn', ''))
                    })

                offset += limit

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        finally:
            logger.info(f"Total jobs fetched from {self.site_name}: {len(jobs)}")
            if len(jobs) == 0:
                logger.error("No jobs found - check API endpoint validity or response format")

        return jobs