import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher
import logging

logger = logging.getLogger(__name__)

class OptiverFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Optiver",
            url="https://optiver.com/working-at-optiver/career-opportunities"
        )
        self.base_url = "https://optiver.com/working-at-optiver/career-opportunities/page/{page}/"

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            # Get initial page to determine total pages
            initial_page = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            initial_page.raise_for_status()
            soup = BeautifulSoup(initial_page.content, 'html.parser')
            
            total_pages = self._get_total_pages(soup)
            logger.info(f"Fetching {total_pages} pages from {self.site_name}")
            jobs = []
            
            # Iterate through all pages
            for page in range(1, total_pages + 1):
                page_url = self.base_url.format(page=page)
                response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                
                page_soup = BeautifulSoup(response.content, 'html.parser')
                jobs.extend(self._parse_page(page_soup))
                
            return jobs

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
            raise

    def _get_total_pages(self, soup: BeautifulSoup) -> int:
        pagination = soup.find('div', class_='pagination')
        if not pagination:
            logger.warning(f"No pagination found for {self.site_name}, using single page")
            return 1
            
        page_links = pagination.find_all('a', class_='page-numbers')
        numeric_pages = [int(link.text) for link in page_links if link.text.isdigit()]
        return max(numeric_pages) if numeric_pages else 1

    def _parse_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        jobs = []
        job_container = soup.find('div', class_='result items items-viewmode-list')
        job_list = job_container.find('ul', class_='result-list') if job_container else None
        if not job_list:
            logger.warning(f"No job list found in {self.site_name} page")
            return jobs

        items = job_list.select('ul.result-list > li')
        logger.info(f"Found {len(items)} job items in page")
        for item in items:
            try:
                # Find main job item container
                # Find elements within container
                main_div = item.select_one('li.php-result-item > div')
                title_tag = main_div.find('h5', class_='h5') if main_div else None
                link_tag = title_tag.find('a') if title_tag else None
                location_tag = main_div.find('p', class_='text-s') if main_div else None
                location_parts = location_tag.get_text(strip=True).split('•') if location_tag else []

                # Detailed missing element detection
                missing = []
                if not title_tag: missing.append("title")
                if not link_tag: missing.append("link")
                if not location_tag: missing.append("location")
                if missing:
                    raise ValueError(f"Missing elements: {', '.join(missing)}")

                jobs.append({
                    'title': title_tag.get_text(strip=True),
                    'url': link_tag['href'],
                    'department': location_parts[0].strip() if location_parts else '',
                     'location': location_parts[1].strip() if len(location_parts) > 1 else '',
                    'posted_date': None,
                    'description': self._build_description(item)
                })
            except Exception as e:
                logger.warning(f"Error parsing job item: {str(e)}")
                raise

        return jobs

    def _build_description(self, item: Any) -> str:
        main_div = item.select_one('li.php-result-item > div')
        if not main_div:
            return ''

        main_section = main_div.find('main')
        elements = [
            main_section.find('span') if main_section else None,
            main_div.find('footer')
        ]
        
        descriptions = []
        for elem in elements:
            if elem:
                descriptions.append(elem.get_text(strip=True))
        role_type_elem = main_div.find('p', class_='text-term')
        role_type = role_type_elem.get_text(strip=True) if role_type_elem else ''
        
        # Get department from location element in current item
        loc_tag = item.find('p', class_='text-s')
        loc_parts = loc_tag.get_text(strip=True).split('•') if loc_tag else []
        department = loc_parts[0].strip() if loc_parts else ''
        if role_type:
            descriptions.insert(0, f"{role_type}: {department}")
        return '\n'.join(descriptions)