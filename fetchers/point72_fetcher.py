import requests
import logging
import json
import ast
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

import re

class Point72Fetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Point72",
            url="https://careers.point72.com/?_gl=1*1u1k88n*_ga*MTc3NDQ2NTE3NS4xNzMwOTg3NTc3*_ga_DP94T093JK*MTc0NTIxNTQ0Mi4xLjEuMTc0NTIxNTYxOC4wLjAuMA.."
        )
        self.session = requests.Session()
        self.session.verify = False

    

    def _clean_html_description(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in ['script', 'style', 'img', 'link']:
            for element in soup.find_all(tag):
                element.decompose()
        text = soup.get_text(separator='\n')
        return '\n'.join(line.strip() for line in text.split('\n') if line.strip())

    def extract_between_quotes(self, input_string: str):
        # Find the index of the first single quote
        first_quote_index = input_string.find("'")
        if first_quote_index == -1:
            return None

        # Find the index of the second single quote
        second_quote_index = input_string.find("',", first_quote_index + 1)
        if second_quote_index == -1:
            return None

        # Extract the substring between the first and second single quotes
        return input_string[first_quote_index + 1:second_quote_index]

    def json_str_cleanup(self, raw_string: str) -> str:
        cleaned = raw_string.replace('\\\\', '__BACKSLASH__')
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace('__BACKSLASH__', '\\')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = re.sub(r'"Job_Description_External__c":.*?"Company__c"', '"Job_Description_External__c":"","Company__c"', cleaned)
        return cleaned

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        response = self.session.get(
            self.url,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', string=lambda t: 'CSSearchModule.init' in (t or ''))
        
        if not script:
            raise ValueError("Job data script not found")

        json_str = self.json_str_cleanup(self.extract_between_quotes(script.text))
        if not json_str:
            logger.error(f"Script content: {script.text[:2000]}")
            raise ValueError("Job data pattern not found in script")

        try:
            job_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {str(e)}") from e

        for item in job_data:
            job = item['job']
            
            if 'Apply_Now_URL__c' not in job:
                logger.warning(f"Job URL not found for job: {job['Name']}")

            jobs.append({
                'title': job['Name'],
                'description': job['Name'] + " - " + item['formattedLocation'],
                'url': job.get('Apply_Now_URL__c', 'https://careers.point72.com/'),
                'location': item['formattedLocation'],
                'posted_date': datetime.strptime(item['lastModifiedDateFormatted'], '%Y-%m-%d')
            })

        logger.info(f"Successfully fetched {len(jobs)} jobs from {self.site_name}")

        return jobs