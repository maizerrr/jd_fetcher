import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class VeritionCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Verition Capital",
            url="https://job-boards.greenhouse.io/embed/job_board?for=veritiongroupllc"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            main_container = soup.select_one('div.job-posts')
            if not main_container:
                return jobs

            for department in main_container.select('div.job-posts--table--department'):
                dept_header = department.select_one('h3.section-header.font-primary')
                dept_name = dept_header.get_text(strip=True) if dept_header else 'General'

                for job_row in department.select('tr.job-post'):
                    link = job_row.select_one('td.cell a[href]')
                    if not link:
                        continue

                    title_elem = link.select_one('p.body.body--medium')
                    location_elem = link.select_one('p.body.body__secondary.body--metadata')

                    jobs.append({
                        'title': title_elem.get_text(strip=True) if title_elem else '',
                        'description': f"{dept_name} - {title_elem.get_text(strip=True) if title_elem else ''}",
                        'url': link['href'],
                        'location': location_elem.get_text(strip=True) if location_elem else '',
                        'posted_date': None  # Date not available in HTML structure
                    })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs