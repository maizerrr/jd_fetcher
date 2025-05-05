import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class HudsonRiverTradingFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Hudson River Trading",
            url="https://www.hudsonrivertrading.com/careers/"
        )
        self.session = requests.Session()

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table', {'class': 'jobs-container'})
            if not table:
                logger.error("Job table not found in HTML")
                return []

            for row in table.find_all('tr', {'class': 'job-row'}):
                try:
                    title_elem = row.find('span', {'class': 'job-title'})
                    url_elem = row.find('a', {'class': 'job-url'})
                    location_elem = row.find('span', {'class': 'job-location-name'})

                    if not all([title_elem, url_elem, location_elem]):
                        logger.warning("Missing required job elements in row")
                        continue

                    jobs.append({
                        'title': title_elem.text.strip(),
                        'description': title_elem.text.strip(),  # Temporary placeholder
                        'url': f"https:{url_elem['href']}" if url_elem['href'].startswith('//') else url_elem['href'],
                        'location': location_elem.text.strip(),
                        'posted_date': datetime.utcnow()
                    })
                except Exception as e:
                    logger.warning(f"Error processing job row: {str(e)}")

            logger.info(f"Successfully fetched {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to fetch jobs: {str(e)}")
        
        return jobs