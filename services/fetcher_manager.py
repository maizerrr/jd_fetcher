import logging
from typing import Dict, List, Any, Union
from models import Job, db
from datetime import datetime

# Import all fetchers (exclude demo fetchers for now)
from fetchers.qube_rt_fetcher import QubeRTFetcher
from fetchers.acadian_fetcher import AcadianAssetManagementFetcher
from fetchers.northrock_fetcher import NorthRockFetcher
from fetchers.quantedge_fetcher import QuantedgeFetcher
from fetchers.lmr_partners_fetcher import LMRPartnersFetcher
from fetchers.graham_capital_fetcher import GrahamCapitalFetcher

logger = logging.getLogger(__name__)

class FetcherManager:
    def __init__(self):
        # Replace demo fetchers with real implementation
        self.fetchers = [
            # QubeRTFetcher(),
            # AcadianAssetManagementFetcher(),
            # NorthRockFetcher(),
            # QuantedgeFetcher(),
            # LMRPartnersFetcher(),
            GrahamCapitalFetcher()
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
        Store fetched jobs in the database. Replaces all existing jobs for this site.
        Uses SQLAlchemy session with atomic transaction.
        """
        try:
            # Delete all existing jobs for this site first
            delete_count = Job.query.filter_by(source_site=site_name).delete()
            logger.info(f"Cleared {delete_count} existing jobs for {site_name}")
            
            # Add all new jobs
            for job_data in jobs:
                new_job = Job(
                    title=job_data['title'],
                    description=job_data['description'],
                    source_site=site_name,  # Ensure consistency with fetcher site
                    url=job_data['url'],
                    location=job_data['location'],
                    posted_date=job_data['posted_date'],
                    updated_time=datetime.utcnow()
                )
                db.session.add(new_job)
            
            # Commit the transaction
            db.session.commit()
            logger.info(f"Successfully stored {len(jobs)} new jobs from {site_name}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing jobs from {site_name}: {str(e)}")
            raise