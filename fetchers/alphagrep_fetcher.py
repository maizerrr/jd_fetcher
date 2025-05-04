import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class AlphagrepFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Alphagrep",
            url="https://www.alpha-grep.com/career/"
        )

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            html = self._get_html()
            soup = BeautifulSoup(html, 'html.parser')
            
            job_list = soup.find('ul', class_='result-list')
            if not job_list:
                raise ValueError("未找到职位列表元素")

            for a_tag in job_list.find_all('a', href=True):
                title_elem = a_tag.find('h5')
                location_elem = a_tag.find('span', class_='jobLocation')
                
                if title_elem and location_elem:
                    # 清理地点中的额外符号
                    location = location_elem.get_text(strip=True).split('<')[0].strip()
                    
                    jobs.append({
                        'title': title_elem.get_text(strip=True),
                        'description': title_elem.get_text(strip=True),
                        'url': a_tag['href'],
                        'location': location,
                        'posted_date': None
                    })

            logger.info(f"成功抓取{len(jobs)}个职位来自{self.site_name}")

        except Exception as e:
            logger.error(f"抓取{self.site_name}职位时出错: {str(e)}")
            raise

        return jobs