from bs4 import BeautifulSoup
import requests
from datetime import datetime
from urllib.parse import urljoin
from .base_fetcher import BaseFetcher

class QuantedgeFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Quantedge Global Master",
            url="https://www.quantedge.com/careers"
        )

    def parse_jobs(self, html: str) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []

        # Find current roles section
        roles_header = soup.find('p', string=lambda text: text and 'We are currently recruiting for the following roles:' in text.strip())
        if not roles_header:
            return jobs

        # Extract job links
        import re
        for link in roles_header.find_all_next('a', href=True):
            href = link['href']
            # Check for career pattern and valid link structure
            if re.match(r'https?://www\.quantedge\.com/careers/.+', href):
                print(f"Link: {href}")
                try:
                    job_url = urljoin(self.url, link['href'])
                    job_page = requests.get(job_url, headers=self.headers, timeout=self.timeout)
                    job_page.raise_for_status()
                    job_soup = BeautifulSoup(job_page.text, 'html.parser')

                    # Extract job details
                    content_elements = job_soup.select('.wixui-rich-text__text')
                    raw_title = content_elements[0].get_text(strip=True) if content_elements else 'Untitled Position'
                    
                    # Parse title with format 'Val1 - Val2 - Val3'
                    # Val2 should be saved as job title, Val3 as location
                    title_parts = raw_title.split(' - ')
                    if len(title_parts) >= 3:
                        job_title = title_parts[1].strip()
                        location = title_parts[2].strip()
                    else:
                        job_title = raw_title
                        location = job_soup.find('div', class_='job-location').get_text(strip=True) if job_soup.find('div', class_='job-location') else 'Singapore'
                    
                    description = '\n'.join([elem.get_text(strip=True, separator='\n') for elem in content_elements[1:] if elem.get_text(strip=True)])

                    jobs.append({
                        'title': job_title,
                        'description': description,
                        'url': job_url,
                        'location': location,
                        'posted_date': datetime.now()
                    })
                except Exception as e:
                    print(f"Error parsing job {job_url}: {str(e)}")

        return jobs