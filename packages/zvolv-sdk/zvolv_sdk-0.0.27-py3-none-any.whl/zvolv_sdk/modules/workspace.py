import requests

class Workspace:
    def __init__(self, session, logger, base_url):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = None
    
    def init(self, domain):
        """Set the domain for the workspace."""
        try:
            if not domain:
                raise ValueError("Domain is required to initialize the workspace")
            self.session.headers.update({'domain': domain})
            """Fetch workspace details from domain."""
            url = f"{self.base_url}/rest/v17/organisation/web/config/{domain}"
            response = self.session.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            resp = response.json()
            if resp.get('error') == False:
                self.workspace_instance = resp['data']
                self.logger.info(f"Workspace initialized: {domain}")
            else:
                raise ValueError(resp.get('message'))
        except Exception as e:
            self.logger.error(e)
            raise e