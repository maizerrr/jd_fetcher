import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_fetcher import BaseFetcher
from requests.exceptions import RequestException
import re
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SusquehannaInvestmentFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Susquehanna International Group",
            url="https://careers.sig.com/global-experienced"
        )

    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Parses HTML content to extract job listings with pagination handling."""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []

        # Get total jobs count
        total_span = soup.find('span', class_='total-jobs')
        if not total_span:
            logger.error("Total jobs element not found")
            return jobs

        try:
            total_jobs = int(total_span.get_text(strip=True))
            pages = range(0, total_jobs, 10)
        except ValueError:
            logger.error("Failed to parse total jobs count")
            return jobs

        # Process initial page
        jobs.extend(self._parse_page(soup))

        # Process subsequent pages
        for offset in pages[1:]:
            page_url = f"{self.url}?from={offset}&s=1&rk=l-global-experienced"
            try:
                response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                page_soup = BeautifulSoup(response.text, 'html.parser')
                jobs.extend(self._parse_page(page_soup))
            except RequestException as e:
                logger.error(f"Failed to fetch page {offset}: {str(e)}")

        return jobs

    def _parse_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parses individual job listings from a page."""
        page_jobs = []
        for item in soup.find_all('li', class_='jobs-list-item'):
            try:
                title_elem = item.find('div', class_='job-title')
                title = title_elem.get_text(strip=True) if title_elem else "No title"

                job_info = item.find('p', class_='job-info')
                location = job_info.find('span', class_='job-location').get_text(strip=True) if job_info else ""
                category = job_info.find('span', class_='job-category').get_text(strip=True) if job_info else ""
                type_info = job_info.find('span', class_='src-only').get_text(strip=True) if job_info else ""

                link = item.find('a', href=True)
                url = urljoin(self.url, link['href']) if link else ""

                page_jobs.append({
                    'title': title,
                    'location': location,
                    'description': f"{location} | {category} | {type_info}",
                    'url': url,
                    'source_site': self.site_name,
                    'posted_date': None
                })
            except Exception as e:
                logger.error(f"Error parsing job item: {str(e)}")

        return page_jobs

    def parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        """Parses HTML content to extract job listings from JSON data."""
        match = re.search(r'"eagerLoadRefineSearch"\s*:\s*({.*?})', html, re.DOTALL)
        if not match:
            logger.error("Failed to find eagerLoadRefineSearch JSON")
            return []

        json_str = match.group(1)
        try:
            # Balance braces to get valid JSON
            brace_count = 1
            end_index = match.start(1) + 1
            while brace_count > 0 and end_index < len(html):
                if html[end_index] == '{': brace_count +=1
                if html[end_index] == '}': brace_count -=1
                end_index +=1
            
            data = json.loads(html[match.start(1):end_index])
            total_jobs = data['totalHits']
            pages = range(0, total_jobs, 10)

            jobs = []
            for offset in pages:
                page_url = f"{self.url}?from={offset}&s=1&rk=l-global-experienced"
                try:
                    response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
                    response.raise_for_status()
                    page_data = self._parse_page(response.text)
                    jobs.extend(page_data)
                except RequestException as e:
                    logger.error(f"Failed to fetch page {offset}: {str(e)}")

            return jobs

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse JSON data: {str(e)}")
            return []

    def _parse_page(self, html: str) -> List[Dict[str, Any]]:
        """Parses individual job listings from JSON data."""
        try:
            match = re.search(r'"eagerLoadRefineSearch"\s*:\s*({)', html)
            if not match:
                return []

            # Balance braces to get valid JSON
            brace_count = 1
            end_index = match.start(1) + 1
            while brace_count > 0 and end_index < len(html):
                if html[end_index] == '{': brace_count += 1
                if html[end_index] == '}': brace_count -= 1
                end_index += 1

            data = json.loads(html[match.start(1):end_index])
            return [{

                'title': job.get('title', ''),
                'location': job.get('address') or job.get('location', ''),

                'description': job.get('description', ''),
                'url': f"https://careers.sig.com/job/{job.get('jobId', '')}" if job.get('jobId') else job.get('applyUrl', ''),
                'source_site': self.site_name,
                'posted_date': self._parse_posted_date(job['postedDate']) if job.get('postedDate') else None,

            } for job in data.get('data', {}).get('jobs', []) if job.get('title')]

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse page JSON: {str(e)}")
            return []

    def _parse_posted_date(self, date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime.strptime(date_str[:10], '%Y-%m-%d') if len(date_str) >= 10 else None