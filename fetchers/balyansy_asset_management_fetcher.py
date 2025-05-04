import requests
import logging
import re
from typing import List, Dict, Any
from .base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)

class BalyansyAssetManagementFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(
            site_name="Balyansy Asset Management",
            url="https://bambusdev.my.site.com/s/sfsites/aura?r=1&aura.ApexAction.execute=1"
        )
        self.headers.update({
            'Referer': 'https://bambusdev.my.site.com/s/',
            'Origin': 'https://bambusdev.my.site.com',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            data = {
                'message': '{"actions":[{"id":"149;a","descriptor":"aura://ApexActionController/ACTION$execute","callingDescriptor":"UNKNOWN","params":{"namespace":"","classname":"BamJobRequisitionInfoDataService","method":"searchJobRequisitions","params":{"isVendorPortal":false,"site":"BAM Website","searchKey":"","locationFilters":[],"departmentFilter":[],"availableLocations":[],"experienceLevelFilter":[]},"cacheable":true,"isContinuation":false}}]}',
                'aura.context': '{"mode":"PROD","fwuid":"c1ItM3NYNWFUOE5oQkUwZk1sYW1vQWg5TGxiTHU3MEQ5RnBMM0VzVXc1cmcxMS4zMjc2OC4z","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":"1237_0DoVReIfuy3txr_WdBjmoQ"},"dn":[],"globals":{},"uad":true}',
                'aura.pageURI': '/s/',
                'aura.token': 'null'
            }

            response = requests.post(
                self.url,
                headers=self.headers,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            json_data = response.json()
            for action in json_data.get('actions', []):
                if action.get('state') == 'SUCCESS':
                    for job in action.get('returnValue', {}).get('returnValue', []):
                        location = next(
                            (loc['Location__r']['External_Name__c'] 
                             for loc in job.get('Job_Requisitions_Locations__r', []) 
                             if loc.get('Location__r')),
                            'Location not specified'
                        )
                        
                        title_slug = re.sub(r'[^a-zA-Z0-9]', '-', job['Name']).strip('-')
                        job_url = f"https://bambusdev.my.site.com/s/details?jobReq={title_slug}_{job['Requisition_Number__c']}"
                        
                        jobs.append({
                            'title': job.get('Name', ''),
                            'description': f"{job.get('Department__c', '')} - {job.get('Experience_Level__c', '')}",
                            'url': job_url,
                            'location': location,
                            'posted_date': None  # Date not available in API response
                        })

        except Exception as e:
            logger.error(f"Error fetching jobs from {self.site_name}: {str(e)}")
        
        return jobs