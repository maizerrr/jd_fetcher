from datetime import datetime
from .base_fetcher import BaseFetcher
from bs4 import BeautifulSoup
import re

class GrahamCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Graham Capital",
            url="https://www.grahamcapital.com/careers/"
        )
    
    def parse_jobs(self, html: str) -> list:
        """Parse HTML to extract job listings from Graham Capital careers page"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Find the section with "What We Do At Graham" heading
        target_heading = soup.find('h2', string='What We Do At Graham')
        if not target_heading:
            return jobs
        
        # Find the accordion section that follows the heading
        # The accordion section is a separate div with class 'image-and-accordions' that follows
        # the div containing the heading
        parent_block = target_heading.find_parent('div', class_='content-block')
        if not parent_block:
            return jobs
            
        # Find the parent section that contains both blocks
        parent_section = parent_block.parent
        if not parent_section:
            return jobs
            
        # Try multiple approaches to find the accordion section
        # First, try to find it as a sibling
        accordion_section = parent_section.find_next_sibling('div', class_='image-and-accordions')
        
        # If not found as a sibling, try to find it within the parent section
        if not accordion_section:
            accordion_section = parent_section.find('div', class_='image-and-accordions')
            
        # If still not found, try to find it anywhere after the heading in the document
        if not accordion_section:
            accordion_section = target_heading.find_next('div', class_='image-and-accordions')
            
        if not accordion_section:
            return jobs
        
        # Find all accordion rows within the section
        # Navigate through the nested structure to find the accordion rows
        accordions_wrapper = accordion_section.find('div', class_='accordions-wrapper')
        if not accordions_wrapper:
            return jobs
            
        accordion_rows = accordions_wrapper.find_all('div', class_='accordion-row')

        for row in accordion_rows:
            try:
                # Extract job title from h3 element
                title_element = row.find('h3')
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                
                # Extract job description from accordion content
                description = ""
                content_div = row.find('div', class_='accordion-content')
                if content_div:
                    # Get all text from the content div
                    description = content_div.get_text(strip=True)
                
                # Create job entry
                jobs.append({
                    'title': title,
                    'description': description,
                    'source_site': self.site_name,
                    'url': self.url,  # Use the careers page URL for all jobs
                    'location': 'Rowayton, CT',  # Fixed location as specified
                    'posted_date': datetime.now()  # Use current date as posting date
                })
            except Exception as e:
                print(f"Error parsing job row: {str(e)}")
        
        return jobs