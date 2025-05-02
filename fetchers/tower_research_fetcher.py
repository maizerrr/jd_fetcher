import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class TowerResearchFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Tower Research",
            url="https://job-boards.greenhouse.io/embed/job_board?for=towerresearchcapital"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # Get total pages
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pagination = soup.find('div', {'class': 'pagination-wrapper'})
            max_page = max(
                [int(li.button.text.strip()) for li in pagination.ul.find_all('li') if li.button]
            ) if pagination else 1

            # Iterate through pages
            for page in range(1, max_page + 1):
                page_url = f"{self.url}&page={page}"
                page_response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                page_response.raise_for_status()
                page_soup = BeautifulSoup(page_response.content, 'html.parser')

                # Process departments
                for department in page_soup.find_all('div', {'class': 'job-posts--table--department'}):
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
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs