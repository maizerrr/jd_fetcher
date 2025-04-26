from datetime import datetime
import requests
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher
import logging

logger = logging.getLogger(__name__)

class WintonCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="WintonCapital",
            url="https://www.winton.com/opportunities"
        )
    
    def parse_jobs(self, html: str) -> list:
        jobs = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main container
        main_element = soup.find('main', attrs={'role': 'main', 'class': 'relative'})
        if not main_element:
            logger.error("Main element not found on Winton Capital page")
            return jobs
        
        # Find the job listing container (fourth child of main)
        job_container = None
        children = list(main_element.find_all(recursive=False))
        if len(children) >= 4:
            job_container = children[3]
        
        if not job_container:
            logger.error("Job container not found on Winton Capital page")
            return jobs
        
        # Find all job rows (div elements with py-10 class in their class list)
        job_rows = job_container.find_all('div', class_=lambda c: c and 'py-10' in c)
        
        for job_row in job_rows:
            try:
                # Extract job title from the first h4 element
                title_element = job_row.find('h4')
                title = title_element.get_text(strip=True) if title_element else "Unknown Title"
                
                # Extract location from the h5 element
                location_element = job_row.find('h5')
                location = location_element.get_text(strip=True) if location_element else "Unknown Location"
                
                # Extract apply link
                apply_link_element = job_row.find('a', class_=lambda c: c and 'btn' in c)
                apply_link = apply_link_element.get('href') if apply_link_element else None
                
                if not apply_link:
                    logger.warning(f"No apply link found for job: {title}")
                    continue
                
                # Fetch job description from the detail page
                description = self._fetch_job_description(apply_link)
                
                jobs.append({
                    'title': title,
                    'description': description,
                    'source_site': self.site_name,
                    'url': apply_link,
                    'location': location,
                    'posted_date': datetime.now()  # Use current date as posted date since not provided
                })
                
            except Exception as e:
                logger.error(f"Error parsing job row: {str(e)}")
        
        return jobs
    
    def _fetch_job_description(self, job_url: str) -> str:
        """Fetch and parse the job description from the detail page"""
        try:
            response = requests.get(job_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            detail_soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main content element
            main_element = detail_soup.find('main', attrs={'role': 'main', 'class': 'relative'})
            if not main_element:
                return "No description available"
            
            # Extract text from all paragraph elements
            paragraphs = main_element.find_all('p')
            paragraph_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            
            # Extract text from all list items
            list_items = main_element.find_all('li')
            list_item_texts = [f"• {li.get_text(strip=True)}" for li in list_items if li.get_text(strip=True)]
            
            # Combine all text elements
            all_texts = paragraph_texts + list_item_texts
            description = "\n\n".join(all_texts)
            
            return description if description else "No description available"
            
        except Exception as e:
            logger.error(f"Error fetching job description from {job_url}: {str(e)}")
            return f"Error fetching description: {str(e)}"