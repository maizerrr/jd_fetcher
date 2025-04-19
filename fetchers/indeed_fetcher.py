from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from .base_fetcher import BaseFetcher

class IndeedFetcher(BaseFetcher):
    def __init__(self):
        # In a real implementation, this would be a valid Indeed jobs search URL
        super().__init__(site_name="Indeed", url="https://www.indeed.com/jobs")
    
    def parse_jobs(self, html: str):
        """
        Parse Indeed job listings from HTML content.
        Returns a list of job dictionaries.
        """
        jobs = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # This is a simplified example - actual Indeed parsing would be more complex
        # and would need to adapt to their HTML structure
        job_cards = soup.find_all('div', class_='jobsearch-ResultsList')
        
        for card in job_cards:
            try:
                # Extract job details
                title_elem = card.find('h2', class_='jobTitle')
                company_elem = card.find('span', class_='companyName')
                desc_elem = card.find('div', class_='job-snippet')
                date_elem = card.find('span', class_='date')
                
                # Get job URL
                link_elem = card.find('a', class_='jcs-JobTitle')
                base_url = "https://www.indeed.com"
                url = base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
                
                # Process data
                title = title_elem.text.strip() if title_elem else 'Unknown Title'
                
                # Create description from available elements
                description_parts = []
                if company_elem:
                    description_parts.append(f"Company: {company_elem.text.strip()}")
                if desc_elem:
                    description_parts.append(desc_elem.text.strip())
                description = ' | '.join(description_parts) or 'No description available'
                
                # Parse date - this is simplified and would need to match Indeed's format
                posted_date = None
                if date_elem:
                    date_text = date_elem.text.strip().lower()
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if 'today' in date_text:
                        posted_date = today
                    elif 'yesterday' in date_text:
                        posted_date = today - timedelta(days=1)
                    elif 'days ago' in date_text:
                        days = int(re.search(r'(\d+)', date_text).group(1))
                        posted_date = today - timedelta(days=days)
                    else:
                        # Default to today if we can't parse the date
                        posted_date = today
                
                # Add job to results
                jobs.append({
                    'title': title,
                    'description': description,
                    'source_site': self.site_name,
                    'url': url,
                    'posted_date': posted_date
                })
                
            except Exception as e:
                # Log error but continue processing other jobs
                print(f"Error parsing job card: {str(e)}")
        
        return jobs