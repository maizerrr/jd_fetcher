from datetime import datetime
from urllib.parse import urlparse, parse_qs
from .base_fetcher import BaseFetcher
import json
import re

class AcadianAssetManagementFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="AcadianAssetManagement",
            url="https://job-boards.greenhouse.io/embed/job_board?for=acadianassetmanagementllc&_data=routes%2Fembed.job_board"
        )

    def parse_jobs(self, html: str) -> list:
        jobs_data = json.loads(html)
        jobs = []

        for job in jobs_data.get('jobPosts', {}).get('data', []):
            try:
                parsed_url = urlparse(job.get('absolute_url', ''))
                gh_jid = parse_qs(parsed_url.query).get('gh_jid', [None])[0]

                jobs.append({
                    'title': f"{job.get('department', {}).get('name', 'N/A')} - {job.get('title', 'Unknown Title')}",
                    'description': self._clean_html_content(job.get('content', '')),
                    'source_site': self.site_name,
                    'url': f"https://www.acadian-asset.com/careers/open-positions?gh_jid={gh_jid}" if gh_jid else job.get('absolute_url', ''),
                    'posted_date': self._parse_datetime(job.get('published_at')),
                    'location': job.get('location', 'Unknown')
                })
            except Exception as e:
                print(f"Error parsing job {job.get('id')}: {str(e)}")

        return jobs

    def _build_description(self, job: dict) -> str:
        desc_parts = [
            f"Location: {job.get('location', 'Unknown')}",
            f"Department: {job.get('department', {}).get('name', 'N/A')}"
        ]
        if job.get('requisition_id'):
            desc_parts.append(f"Requisition ID: {job.get('requisition_id')}")
        return '\n'.join(desc_parts)

    def _clean_html_content(self, raw_html: str) -> str:
        """Clean HTML entities and tags from job description content"""
        if not raw_html:
            return ""
            
        # Replace common HTML entities
        replacements = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&nbsp;': ' ',
            '\u00a0': ' '  # Unicode non-breaking space
        }
        for entity, replacement in replacements.items():
            raw_html = raw_html.replace(entity, replacement)
        
        # Remove HTML tags using regex (safe for simple content)
        clean_text = re.sub(r'<.*?>', '', raw_html)
        
        # Collapse multiple newlines and whitespace
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        return clean_text.strip()

    def _parse_datetime(self, iso_str: str) -> datetime:
        if not iso_str:
            return datetime.now()
        try:
            return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        except ValueError:
            return datetime.now()