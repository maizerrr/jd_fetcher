import requests
import logging
import json
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class DRWFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="DRW",
            url="https://www.drw.com/work-at-drw/listings"
        )

    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            raise ValueError("__NEXT_DATA__ script tag not found")
        data = json.loads(script_tag.string)['props']
        
        jobs_data = data.get('pageProps', {}).get('jobData', {}).get('en', [])
        
        if not jobs_data:
            raise ValueError("No job data found in HTML script")

        jobs = []
        logger.info(f"Found {len(jobs_data)} jobs")
        for job in jobs_data:
            if not job.get('slug'):
                raise ValueError("Missing slug in job data")
            
            category = job.get('career_categories', [''])
            primary_category = category[0] if category else ''
            
            jobs.append({
                'title': job.get('job_title', ''),
                'description': f"{primary_category} - {job.get('job_title', '')}",
                'url': f"https://www.drw.com/work-at-drw/listings/{job.get('slug')}",
                'location': ', '.join(job.get('locations', [])),
                'posted_date': datetime.utcnow()
            })
            
        return jobs