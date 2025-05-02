import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class WorldQuantFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="WorldQuant",
            url="https://www.worldquant.com/career-listing/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        jobs = []
        careers_list = soup.find('ul', {'id': 'careers_list', 'class': 'cg-list'})
        
        if careers_list:
            for li in careers_list.find_all('li'):
                link = li.find('a', class_='fo-link')
                if not link:
                    continue

                # Extract job ID from href
                href = link.get('href', '')
                job_id = href.split('id=')[-1] if 'id=' in href else ''

                # Get title from h4
                title_elem = link.find('h4', class_='h4')
                title = title_elem.get_text(strip=True) if title_elem else ''

                # Get location from data attribute
                location = li.get('data-location', '').replace('-', ' ').replace('|', ', ')

                jobs.append({
                    'title': title,
                    'url': f"https://www.worldquant.com/career-listing/?id={job_id}",
                    'location': location,
                    'posted_date': None,
                    'description': title  # Description not available in listing
                })

        return jobs