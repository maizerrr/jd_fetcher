import requests
import logging
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class JumpTradingFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Jump Trading",
            url="https://www.jumptrading.com/careers/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            html = self._get_html()
            soup = BeautifulSoup(html, 'html.parser')
            
            a_tags = []
            for a_tag in soup.find_all('a', {'role': 'listitem', 'href': True}):
                href = a_tag['href']
                if not re.match(r'^/careers/\d+/$', href):
                    continue
                a_tags.append(a_tag)

            logger.info(f"Found {len(a_tags)} job listings on {self.site_name}")

            for a_tag in a_tags:
                title_elem = a_tag.select_one('p[class*="text-xl"][class*="lg:text-2xl"][class*="font-medium"]')
                location_elem = a_tag.select_one('p[class*="text-base"][class*="lg:text-lg"][class*="text-dark-gray"]')

                if title_elem and location_elem:
                    jobs.append({
                        'title': title_elem.get_text(strip=True),
                        'description': title_elem.get_text(strip=True),
                        'url': f"https://www.jumptrading.com{href}",
                        'location': location_elem.get_text(strip=True),
                        'posted_date': None
                    })
                else:
                    raise ValueError(f"job title (is none? {title_elem is None}) and location (is none? {location_elem is None}) must not be None, {self.site_name}")

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            raise
        
        return jobs