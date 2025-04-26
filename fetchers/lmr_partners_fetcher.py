from datetime import datetime
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

class LMRPartnersFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="LMR Multi-Strategy",
            url="https://www.lmrpartners.com/careers"
        )
    
    def parse_jobs(self, html: str) -> list:
        """Parse HTML to extract job listings from LMR Partners careers page"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Find all card elements that contain job listings
        card_elements = soup.find_all(class_=lambda c: c and c.startswith('style_card_'))
        if not card_elements:
            # Fallback to the specific class name provided in the example
            card_elements = soup.find_all(class_='style_card__Dp9RX')
        
        for card in card_elements:
            try:
                # Extract job title from the first h5 element
                title_element = card.find('h5')
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                
                # Extract description from the remaining content
                description = ""
                p_elements = card.find_all('p')
                if p_elements:
                    description = '\n'.join([p.get_text(strip=True) for p in p_elements])
                
                jobs.append({
                    'title': title,
                    'description': description,
                    'source_site': self.site_name,
                    'url': "https://www.lmrpartners.com/careers",  # Fixed URL as requested
                    'location': "",  # Leave location blank as requested
                    'posted_date': datetime.now()  # No date info available, use current date
                })
            except Exception as e:
                print(f"Error parsing job card: {str(e)}")
        
        return jobs