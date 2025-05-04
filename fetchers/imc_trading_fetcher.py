import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class IMCTradingFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="IMC Trading",
            url="https://www.imc.com/ap/search-careers"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # Get total pages
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pagination buttons and extract max page number
            page_buttons = soup.select('button.flquq3c:not([disabled])')
            max_page = max(
                (int(btn.text) for btn in page_buttons if btn.text.isdigit()),
                default=1
            )
            logger.info(f"Detected {max_page} total pages for {self.site_name}")

            # Iterate through pages
            for page in range(1, max_page + 1):
                page_url = f"{self.url}?page={page}"
                logger.debug(f"Processing page {page} - {page_url}")
                page_response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                job_cards = page_soup.select('a[href^="/ap/careers/jobs/"]')
                logger.info(f"Page {page}/{max_page}: Found {len(job_cards)} potential job links")

                # Extract job cards
                for job_card in job_cards:
                    title_elem = job_card.select_one('h2._13fp8yk6c')
                    location_elem = job_card.select_one('svg + span._13fp8yk6c')
                    
                    if title_elem and location_elem:
                        jobs.append({
                            'title': title_elem.get_text(strip=True),
                            'description': f"{title_elem.get_text(strip=True)} - {location_elem.get_text(strip=True)}",
                            'url': f"https://www.imc.com{job_card['href']}",
                            'location': location_elem.get_text(strip=True),
                            'posted_date': None
                        })
                    else:
                        missing = []
                        if not title_elem: missing.append("title")
                        if not location_elem: missing.append("location")
                        logger.warning(f"job card {job_card['href']} missing {', '.join(missing)}")

            logger.info(f"Collected total {len(jobs)} jobs from {max_page} pages (validation rate: {len(jobs)/sum(len(p) for p in job_cards):.1%})")

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs