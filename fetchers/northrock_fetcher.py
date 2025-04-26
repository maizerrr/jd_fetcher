from datetime import datetime
from .base_fetcher import BaseFetcher
import json

class NorthRockFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="NorthRock",
            url="https://secure6.saashr.com/ta/rest/ui/recruitment/companies/%7C6186483/job-requisitions?offset=1&size=20&sort=desc&ein_id=&lang=en-US"
        )

    def parse_jobs(self, response: str) -> list:
        jobs_data = json.loads(response)
        jobs = []

        for job in jobs_data.get('job_requisitions', []):
            try:
                jobs.append({
                    'title': job.get('job_title', 'Unknown Title'),
                    'description': job.get('job_description', 'No description available'),
                    'source_site': self.site_name,
                    'url': f"https://secure6.saashr.com/ta/6186483.careers?ApplyToJob={job.get('id')}&LanguageOverride=EN",
                    'location': f"{job.get('location', {}).get('city', '')}, {job.get('location', {}).get('state', '')}".strip(', '),
                    'posted_date': datetime.now()
                })
            except Exception as e:
                print(f"Error parsing job {job.get('id')}: {str(e)}")

        return jobs