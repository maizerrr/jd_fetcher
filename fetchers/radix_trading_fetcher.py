import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class RadixTradingFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Radix Trading LLC",
            url="https://job-boards.greenhouse.io/radixuniversity" # dummy url to satisfy the parent class
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        for url in ['https://job-boards.greenhouse.io/radixuniversity', 'https://job-boards.greenhouse.io/radixexperienced']:
            try:
                response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                container = soup.find('div', {'class': 'job-posts'})
                if not container:
                    raise ValueError("Job posts container not found.")

                for department in container.find_all('div', {'class': 'job-posts--table--department'}):
                    dept_name = department.h3.text.strip()
                    
                    for job in department.find_all('tr', {'class': 'job-post'}):
                        link = job.find('a')
                        title = link.find('p', {'class': 'body--medium'}).text.strip()
                        location = link.find('p', {'class': 'body__secondary'}).text.strip()

                        jobs.append({
                            'title': title,
                            'description': f"{dept_name}: {title}",
                            'url': link['href'],
                            'location': location,
                            'posted_date': None
                        })

            except Exception as e:
                logger.error(f"Error fetching jobs from {url}: {str(e)}")
        
        return jobs