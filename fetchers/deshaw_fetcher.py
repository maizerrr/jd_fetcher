import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class DEShawFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="D.E. Shaw",
            url="https://www.deshaw.com/careers/choose-your-path"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        jobs = []
        job_elements = soup.find_all('div', class_='job')
        
        if not job_elements:
            raise ValueError("No job elements found in HTML")

        logger.info(f"Found {len(job_elements)} jobs")
        
        for job in job_elements:
            try:
                title_elem = job.find('span', class_='job-display-name')
                if not title_elem:
                    raise ValueError("Missing job title element")
                
                category_elem = job.find('p', class_='category')
                location_elem = job.find('span', class_='location')
                link_elem = job.find('a', class_='parent-arrow-long')

                jobs.append({
                    'title': title_elem.text.strip(),
                    'description': f"{category_elem.text.strip() if category_elem else ''} - {title_elem.text.strip()}",
                    'url': f"https://www.deshaw.com{link_elem['href']}" if link_elem else '',
                    'location': location_elem.text.strip() if location_elem else 'Remote',
                    'posted_date': datetime.utcnow()
                })
            except Exception as e:
                logger.error(f"Error processing job element: {str(e)}")
                continue

        return jobs