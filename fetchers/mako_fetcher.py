from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher
from datetime import datetime

class MakoFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(site_name='Mako', url='https://www.mako.com/opportunities#jobs')

    def fetch_jobs(self):
        html = self._get_html()
        soup = BeautifulSoup(html, 'html.parser')
        
        jobs = []
        for item in soup.select('div.job-entry'):
            job_data = {
                'title': item.select_one('h3.job-heading').text.strip(),
                'url': (link['href'] if (link := item.select_one('div.job-button a')) else ''),
                'location': (loc.text.strip() if (loc := item.select_one('.is_location')) else ''),
                'department': (dept.text.strip() if (dept := item.select_one('.is_dept')) else ''),
                'posted_date': None,
                'description': f"Department: {dept.text.strip()}" if (dept := item.select_one('.is_dept')) else 'Department: Not specified'
            }
            jobs.append(job_data)
        return jobs