import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class TwoSigmaFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Two Sigma",
            url="https://careers.twosigma.com/careers/OpenRoles"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        nav = soup.find('nav', {'aria-label': 'Pagination Navigation'})
        page_elements = nav.find_all(['a', 'span'], class_=lambda x: x in ['paginationLink', 'currentPageLink'])
        page_numbers = []
        for e in page_elements:
            text_parts = e.text.strip().split()
            if text_parts and text_parts[-1].isdigit():
                page_numbers.append(int(text_parts[-1]))
        max_page = max(page_numbers) if page_numbers else 1
        logger.info(f"Found {max_page} pages of jobs.")

        for page in range(1, max_page + 1):
            page_url = f"{self.url}/?jobRecordsPerPage=10&jobOffset={(page-1)*10}"
            page_response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
            page_response.raise_for_status()
            
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            results_panel = page_soup.find('div', class_='results__panel')
            
            for article in results_panel.find_all('article', class_='article--result'):
                header = article.find('h3', class_='article__header__text__title')
                footer = article.find('div', class_='article__footer')
                url = footer.find('a', class_='button--secondary')['href'] if footer else ''
                
                location_span = article.find('span', class_='paragraph_inner-span')
                sub_text = article.find('div', class_='article__header__content__sub-text')
                spans = sub_text.find_all('span', class_='paragraph_inner-span') if sub_text else []
                department = spans[0].text if len(spans) > 0 else 'N/A'
                experience = next((s.text for s in spans if 'experienced' in s.text.lower()), 'N/A')
                
                jobs.append({
                    'title': header.text.strip(),
                    'description': f"Department: {department}\nExperience: {experience}",
                    'url': url,
                    'location': location_span.text.split(' - ')[-1].strip(),
                    'posted_date': datetime.utcnow()
                })
        
        return jobs