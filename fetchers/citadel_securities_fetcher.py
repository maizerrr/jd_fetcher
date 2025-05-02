import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class CitadelSecuritiesFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Citadel Securities",
            url="https://www.citadelsecurities.com/careers/open-opportunities/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # Get initial page to determine total pages
            initial_page = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            initial_page.raise_for_status()
            soup = BeautifulSoup(initial_page.content, 'html.parser')
            
            # Extract total jobs count
            total_jobs = int(soup.find('span', {'class': 'total-post'}).text.strip().split()[0])
            total_pages = (total_jobs // 10) + (1 if total_jobs % 10 else 0)

            # Iterate through pagination
            for page in range(1, total_pages + 1):
                page_url = f"{self.url}page/{page}/"
                response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                
                page_soup = BeautifulSoup(response.content, 'html.parser')
                cards = page_soup.find_all('a', {'class': 'careers-listing-card'})
                
                for card in cards:
                    job_url = card['href']
                    try:
                        detail_res = requests.get(job_url, headers=self.headers, timeout=self.timeout)
                        detail_res.raise_for_status()
                        detail_soup = BeautifulSoup(detail_res.content, 'html.parser')
                        description = detail_soup.find('div', {'class': 'careers-details__content'}).text.strip()
                    except Exception as e:
                        logger.warning(f"Failed to fetch details for {job_url}: {str(e)}")
                        description = ''
                    
                    jobs.append({
                        'title': card.find('h2').text.strip(),
                        'location': card.find('div', {'class': 'careers-listing-card__location'}).text.strip(),
                        'url': job_url,
                        'description': description,
                        'posted_date': None
                    })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs