from datetime import datetime
from .base_fetcher import BaseFetcher
import json
import re

class AspectCapitalFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Aspect Capital",
            url="https://aspectcapital-94a5ce.careers.hibob.com/api/job-ad"
        )
        self.headers = {
            "Companyidentifier": "aspectcapital-94a5ce"
        }

    def parse_jobs(self, response: str) -> list:
        jobs_data = json.loads(response)
        jobs = []

        for job in jobs_data.get('jobAdDetails', []):
            try:
                cleaned_description = self._clean_html_content(job.get('description', ''))
                cleaned_requirements = self._clean_html_content(job.get('requirements', ''))
                cleaned_responsibilities = self._clean_html_content(job.get('responsibilities', ''))
                combined_description = f"{cleaned_description}\n\nRequirements:\n{cleaned_requirements}\n\nResponsibilities:\n{cleaned_responsibilities}"
                jobs.append({
                    'title': job.get('title', 'Unknown Title'),
                    'description': combined_description,
                    'source_site': self.site_name,
                    'url': f"https://aspectcapital-94a5ce.careers.hibob.com/job/{job.get('id')}",
                    'location': f"{job.get('site', '')}, {job.get('country', '')}".strip(', '),
                    'posted_date': datetime.fromisoformat(job.get('publishedAt', datetime.now().isoformat()).split('.')[0].replace('Z', '+00:00'))
                })
            except Exception as e:
                print(f"Error parsing job {job.get('id')}: {str(e)}")

        return jobs

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