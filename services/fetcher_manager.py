import logging
from typing import Dict, List, Any, Union
from models import Job, db
from datetime import datetime

# Import all fetchers
from fetchers.linkedin_fetcher import LinkedInFetcher
from fetchers.indeed_fetcher import IndeedFetcher

logger = logging.getLogger(__name__)

class FetcherManager:
    def __init__(self):
        # Register all fetchers here
        self.fetchers = [
            LinkedInFetcher(),
            IndeedFetcher()
        ]
    
    def fetch_all_jobs(self) -> Dict[str, Union[List[str], Dict[str, str]]]:
        """
        Execute all registered fetchers and store results in database.
        Returns a summary of successful and failed fetchers.
        """
        result = {
            "success": [],
            "failed": {}
        }
        
        for fetcher in self.fetchers:
            try:
                logger.info(f"Starting job fetch from {fetcher.site_name}")
                
                # Fetch jobs from the site
                jobs = fetcher.fetch_jobs()
                
                # Store jobs in database (only if fetch was successful)
                self._store_jobs(fetcher.site_name, jobs)
                
                # Record success
                result["success"].append(fetcher.site_name)
                logger.info(f"Successfully fetched {len(jobs)} jobs from {fetcher.site_name}")
                
            except Exception as e:
                # Log the error
                error_message = str(e)
                logger.error(f"Error fetching jobs from {fetcher.site_name}: {error_message}")
                
                # Record failure
                result["failed"][fetcher.site_name] = error_message
        
        return result
    
    def _store_jobs(self, site_name: str, jobs: List[Dict[str, Any]]) -> None:
        """
        Store fetched jobs in the database.
        Uses SQLAlchemy session with atomic transaction.
        """
        try:
            # Start a new transaction
            for job_data in jobs:
                # Check if job with this URL already exists
                existing_job = Job.query.filter_by(url=job_data['url']).first()
                
                if existing_job:
                    # Update existing job
                    existing_job.title = job_data['title']
                    existing_job.description = job_data['description']
                    existing_job.posted_date = job_data['posted_date']
                    existing_job.updated_time = datetime.utcnow()
                else:
                    # Create new job
                    new_job = Job(
                        title=job_data['title'],
                        description=job_data['description'],
                        source_site=job_data['source_site'],
                        url=job_data['url'],
                        posted_date=job_data['posted_date'],
                        updated_time=datetime.utcnow()
                    )
                    db.session.add(new_job)
            
            # Commit the transaction
            db.session.commit()
            logger.info(f"Successfully stored jobs from {site_name}")
            
        except Exception as e:
            # Roll back the transaction on error
            db.session.rollback()
            logger.error(f"Error storing jobs from {site_name}: {str(e)}")
            raise