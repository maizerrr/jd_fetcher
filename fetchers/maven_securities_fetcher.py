import requests
import logging
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class MavenSecuritiesFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Maven Securities",
            url="https://job-boards.greenhouse.io/embed/job_board?for=mavensecuritiesholdingltd"
        )

    def fetch_jobs(self) -> list[dict[str, any]]:
        jobs = []
        try:
            html = self._get_html()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 处理部门分组
            for department in soup.find_all('div', class_='job-posts--table--department'):
                dept_name = department.find('h3', class_='section-header').text.strip()
                
                for job_row in department.select('tr.job-post'):
                    link = job_row.find('a')
                    if not link:
                        continue
                    
                    jobs.append({
                        'title': link.find('p', class_='body--medium').text.strip(),
                        'description': f"部门：{dept_name}",
                        'url': link['href'],
                        'location': link.find('p', class_='body__secondary').text.strip(),
                        'posted_date': None
                    })

            logger.info(f"成功抓取{len(jobs)}个职位来自{self.site_name}")
            return jobs

        except Exception as e:
            logger.error(f"抓取{self.site_name}职位时发生错误: {str(e)}")
            raise