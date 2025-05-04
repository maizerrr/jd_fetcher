import logging
import concurrent.futures
from typing import Dict, List, Any, Union, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Job, db
from flask import Flask

# Import all fetchers (exclude demo fetchers for now)
from fetchers.qube_rt_fetcher import QubeRTFetcher
from fetchers.acadian_fetcher import AcadianAssetManagementFetcher
from fetchers.northrock_fetcher import NorthRockFetcher
from fetchers.quantedge_fetcher import QuantedgeFetcher
from fetchers.lmr_partners_fetcher import LMRPartnersFetcher
from fetchers.graham_capital_fetcher import GrahamCapitalFetcher
from fetchers.winton_capital_fetcher import WintonCapitalFetcher
from fetchers.aspect_capital_fetcher import AspectCapitalFetcher
from fetchers.viking_global_fetcher import VikingGlobalFetcher
from fetchers.susquehanna_investment_fetcher import SusquehannaInvestmentFetcher
from fetchers.millennium_fetcher import MillenniumFetcher
from fetchers.citadel_securities_fetcher import CitadelSecuritiesFetcher
from fetchers.grasshope_fetcher import GrasshopeFetcher
from fetchers.jane_street_fetcher import JaneStreetFetcher
from fetchers.worldquant_fetcher import WorldQuantFetcher
from fetchers.optiver_fetcher import OptiverFetcher
from fetchers.tower_research_fetcher import TowerResearchFetcher
from fetchers.rockbund_fetcher import RockBundFetcher
from fetchers.trexquant_fetcher import TrexQuantFetcher
from fetchers.jumptrading_fetcher import JumpTradingFetcher
from fetchers.akuna_capital_fetcher import AkunaCapitalFetcher
from fetchers.flow_trader_fetcher import FlowTraderFetcher
from fetchers.eclipse_trading_fetcher import EclipseTradingFetcher
from fetchers.balyansy_asset_management_fetcher import BalyansyAssetManagementFetcher
from fetchers.manahl_fetcher import ManAHLFetcher
from fetchers.verition_capital_fetcher import VeritionCapitalFetcher
from fetchers.imc_trading_fetcher import IMCTradingFetcher
from fetchers.engineersgate_fetcher import EngineersGateFetcher
from fetchers.radix_trading_fetcher import RadixTradingFetcher

logger = logging.getLogger(__name__)

class FetcherManager:
    def __init__(self, app: Flask):
        self.app = app # Store the app instance
        # Replace demo fetchers with real implementation
        self.fetchers = [
            # QubeRTFetcher(),
            # AcadianAssetManagementFetcher(),
            # NorthRockFetcher(),
            # QuantedgeFetcher(),
            # LMRPartnersFetcher(),
            # GrahamCapitalFetcher(),
            # WintonCapitalFetcher(),
            # AspectCapitalFetcher(),
            # VikingGlobalFetcher(),
            # SusquehannaInvestmentFetcher(),
            # MillenniumFetcher(),
            # GrasshopeFetcher(),
            # CitadelSecuritiesFetcher(),
            # JaneStreetFetcher(),
            # WorldQuantFetcher(),
            # OptiverFetcher(),
            # TowerResearchFetcher(),
            # RockBundFetcher(),
            # TrexQuantFetcher(),
            # JumpTradingFetcher(),
            # AkunaCapitalFetcher(),
            # FlowTraderFetcher(),
            # EclipseTradingFetcher(),
            # BalyansyAssetManagementFetcher(),
            # ManAHLFetcher(),
            # VeritionCapitalFetcher(),
            # IMCTradingFetcher(),
            # EngineersGateFetcher(),
            RadixTradingFetcher()
        ]
        self.max_workers = 5 # Adjust the number of workers as needed
    
    def _fetch_and_store_job(self, fetcher) -> Tuple[str, Optional[str]]:
        """Fetches and stores jobs for a single fetcher, handling app context."""
        site_name = fetcher.site_name
        try:
            # Use Flask app context for the entire fetch and store operation
            with self.app.app_context():
                # Check last update time
                min_update = db.session.query(func.min(Job.updated_time))\
                    .filter_by(source_site=site_name)\
                    .scalar()

                if min_update and (datetime.utcnow() - min_update) < timedelta(minutes=self.app.config.get('CACHE_THRESHOLD_MINUTES', 5)):
                    logger.info(f"Skipping {site_name} - all records updated within threshold (oldest update {datetime.utcnow() - min_update} ago)")
                    return site_name, None

                logger.info(f"Starting job fetch from {site_name}")
                jobs = fetcher.fetch_jobs()
                self._store_jobs(site_name, jobs)
                logger.info(f"Successfully fetched and stored {len(jobs)} jobs from {site_name}")
            return site_name, None  # Return site name and no error
        except Exception as e:
            error_message = str(e)
            # Log error outside the explicit context, relying on the outer context if needed
            logger.error(f"Error processing jobs from {site_name}: {error_message}")
            return site_name, error_message # Return site name and error message

    def fetch_all_jobs(self) -> Dict[str, Union[List[str], Dict[str, str]]]:
        """
        Execute all registered fetchers in parallel and store results in database.
        Returns a summary of successful and failed fetchers.
        """
        result = {
            "success": [],
            "failed": {}
        }
        
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map the fetcher processing function to each fetcher
            future_to_fetcher = {executor.submit(self._fetch_and_store_job, fetcher): fetcher for fetcher in self.fetchers}
            
            for future in concurrent.futures.as_completed(future_to_fetcher):
                site_name, error_message = future.result()
                if error_message:
                    result["failed"][site_name] = error_message
                else:
                    result["success"].append(site_name)
                    
        logger.info(f"Finished fetching all jobs. Success: {len(result['success'])}, Failed: {len(result['failed'])}")
        return result
    
    def _store_jobs(self, site_name: str, jobs: List[Dict[str, Any]]) -> None:
        """
        Store fetched jobs in the database. Replaces all existing jobs for this site.
        Store fetched jobs in the database. Replaces all existing jobs for this site.
        Uses SQLAlchemy session with atomic transaction.
        """
        # Ensure database operations run within an application context
        with self.app.app_context():
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