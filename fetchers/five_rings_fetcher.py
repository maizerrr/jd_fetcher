from datetime import datetime
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher  # 假设存在基础爬虫类

class FiveRingsFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(site_name='Five Rings', url='https://fiverings.com/careers/')

    def fetch_jobs(self):
        html = self._get_html()
        soup = BeautifulSoup(html, 'html.parser')
        
        jobs = []
        for item in soup.select('div.gh-item'):
            title_elem = item.select_one('.gh-item_heading a')
            detail_elem = item.select_one('.gh-item_subheading')
            
            job_data = {
                'title': title_elem.text.strip(),
                'url': title_elem['href'],
                'location': item['data-location'],
                'department': item['data-department'],
                'posted_date': datetime.strptime(
                    detail_elem.select_one('span:contains("Posted")').text.replace('Posted ', '').strip(), 
                    '%d-%b-%Y'
                ),
                'description': ' | '.join([
                    f"Department: {item['data-department']}",
                    f"Level: {item['data-level']}"
                ])
            }
            jobs.append(job_data)
        
        return jobs