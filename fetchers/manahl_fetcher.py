import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class ManAHLFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="ManAHL",
            url="https://job-boards.eu.greenhouse.io/mangroup"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # Get total pages
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pagination = soup.select_one('div.pagination-wrapper ul')
            page_buttons = [int(btn.text) for btn in (pagination.select('button.pagination__link') if pagination else []) if btn.text.isdigit()]
            total_pages = max(page_buttons) if page_buttons else 1

            # Iterate through pages
            for page in range(1, total_pages + 1):
                page_url = f"{self.url}?page={page}"
                page_response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                page_response.raise_for_status()
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Process job posts
                for department in page_soup.select('div.job-posts--table--department'):
                    dept_name = department.select_one('h3.section-header').text.strip()
                    
                    for job in department.select('tr.job-post'):
                        link = job.select_one('a[href]')
                        title_elem = job.select_one('p.body--medium')
                        location_elem = job.select_one('p.body--metadata')
                        
                        jobs.append({
                            'title': title_elem.text.strip() if title_elem else '',
                            'description': f"{dept_name} - {title_elem.text.strip() if title_elem else ''}",
                            'url': link['href'] if link else '#',
                            'location': location_elem.text.strip() if location_elem else '',
                            'posted_date': None
                        })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs