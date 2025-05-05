import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class BlueCrestCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="BlueCrest Capital Management",
            url="https://job-boards.greenhouse.io/bluecrestcapitalmanagement"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            main_container = soup.find('div', class_='job-posts')
            if not main_container:
                logger.warning("No job-posts container found")
                return jobs

            for department_section in main_container.find_all('div', class_='job-posts--table--department'):
                department_name = department_section.find('h3', class_='section-header').get_text(strip=True)
                
                for job_row in department_section.select('tr.job-post'):
                    link = job_row.find('a', href=True)
                    if not link:
                        continue

                    title_elem = link.find('p', class_='body--medium')
                    location_elem = link.find('p', class_='body--metadata')

                    jobs.append({
                        'title': title_elem.get_text(strip=True) if title_elem else '',
                        'description': f"{department_name} - {title_elem.get_text(strip=True) if title_elem else ''}",
                        'url': f"https://job-boards.greenhouse.io{link['href']}" if link['href'].startswith('/') else link['href'],
                        'location': location_elem.get_text(strip=True) if location_elem else '',
                        'posted_date': None  # Date not available in HTML structure
                    })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs