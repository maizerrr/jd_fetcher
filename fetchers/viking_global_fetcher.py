import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class VikingGlobalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(site_name="Viking Global", url="https://job-boards.greenhouse.io/vikingglobalinvestors")


    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Parses HTML content to extract job listings for Viking Global."""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        job_tables = soup.find_all('div', class_='job-posts--table')

        if not job_tables:
            logger.warning(f"No job tables found for {self.site_name}")
            return jobs

        for i, table in enumerate(job_tables):
            job_rows = table.find_all('tr', class_='job-post')
            for j, row in enumerate(job_rows):
                cell = row.find('td', class_='cell')
                if not cell:
                    continue
                link_tag = cell.find('a')
                if not link_tag:
                    continue
                
                # Title and Location are inside the link tag
                title_tag = link_tag.find('p', class_='body--medium')
                location_tag = link_tag.find('p', class_='body body__secondary body--metadata')

                if title_tag and location_tag: # Check title and location found within link_tag
                    job_url = link_tag.get('href')
                    if not job_url:
                        logger.warning("Found job row without URL")
                        continue
                    
                    # Ensure the URL is absolute
                    if job_url.startswith('/'):
                         # This case might not happen with greenhouse but good practice
                         from urllib.parse import urljoin
                         job_url = urljoin(self.url, job_url)

                    title = title_tag.get_text(strip=True)
                    location = location_tag.get_text(strip=True)
                    
                    # Fetch and parse the detailed description
                    description = f"{title} - {location}"

                    job_data = {
                        'title': title,
                        'location': location,
                        'url': job_url,
                        'description': description,
                        'source_site': self.site_name,
                        'posted_date': None # Date is not available in the list view
                    }
                    jobs.append(job_data)
                    logger.debug(f"Parsed job: {title} at {location}")
                else:
                    logger.warning("Could not parse all required fields for a job row")

        logger.info(f"Parsed {len(jobs)} jobs from {self.site_name}")
        return jobs