import json
import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class APCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="AP Capital",
            url="https://careers.apcapitalinvestment.com/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script_data = soup.find('script', {'id': '__NEXT_DATA__'})
            
            if script_data:
                json_data = json.loads(script_data.string)
                for job in json_data.get('props', {}).get('pageProps', {}).get('data', []):
                    clean_description = BeautifulSoup(job.get('description', ''), 'html.parser').get_text()
                    
                    jobs.append({
                        'title': job.get('title', ''),
                        'description': clean_description,
                        'url': f"https://careers.apcapitalinvestment.com/job-detail/{job.get('id', '')}",
                        'location': job.get('location', 'Location not specified'),
                        'posted_date': None  # Date not available in JSON structure
                    })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs