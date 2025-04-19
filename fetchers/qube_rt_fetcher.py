from datetime import datetime
from .base_fetcher import BaseFetcher
import json
from urllib.parse import urlparse, parse_qs

class QubeRTFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="QubeRT",
            url="https://boards-api.greenhouse.io/v1/boards/quberesearchandtechnologies/jobs"
        )
    
    def parse_jobs(self, html: str) -> list:
        """Parse JSON response from Greenhouse API"""
        jobs_data = json.loads(html)
        jobs = []
        
        for job in jobs_data.get('jobs', []):
            try:
                # Extract metadata fields
                metadata = {m['name']: m.get('value') for m in job.get('metadata', [])}
                
                original_url = job.get('absolute_url', '')
                parsed_url = urlparse(original_url)
                gh_jid = parse_qs(parsed_url.query).get('gh_jid', [None])[0]
                
                jobs.append({
                    'title': job.get('title', 'Unknown Title'),
                    'description': self._build_description(job, metadata),
                    'source_site': self.site_name,
                    'url': f"https://www.qube-rt.com/careers/job?gh_jid={gh_jid}" if gh_jid else original_url,
                    'posted_date': self._parse_datetime(job.get('first_published')),
                    'updated_at': self._parse_datetime(job.get('updated_at')),
                    'location': job.get('location', {}).get('name', 'Unknown')
                })
            except Exception as e:
                print(f"Error parsing job {job.get('id')}: {str(e)}")
        
        return jobs

    def _build_description(self, job: dict, metadata: dict) -> str:
        """Construct job description from available data"""
        desc_parts = [
            f"Company: {job.get('company_name', 'Qube Research & Technologies')}",
            f"Location: {job.get('location', {}).get('name', 'Unknown')}",
            f"Requisition ID: {job.get('requisition_id', 'N/A')}"
        ]
        
        # Add relevant metadata
        for field in ['Employment Type', 'Candidate Type', 'Experience (for job posting)']:
            if metadata.get(field):
                desc_parts.append(f"{field}: {metadata[field]}")
        
        return '\n'.join(desc_parts)

    def _parse_datetime(self, iso_str: str) -> datetime:
        """Convert ISO 8601 string to datetime object"""
        if not iso_str:
            return datetime.now()
        try:
            return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        except ValueError:
            return datetime.now()