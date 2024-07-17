import requests

from .modules.workspace import Workspace
from .modules.auth import Auth
from .modules.analytics import Analytics
from .modules.forms import Forms
from .modules.submissions import Submissions
from .modules.tasks import Tasks
from .modules.logger import Logger
from .modules.communication import Communication
from .modules.documents import Document

class ZvolvClient:
    def __init__(self, base_url):

        if not base_url:
            raise ValueError("Base URL is required to initialize the client")

        self.base_url = base_url
        self.session = requests.Session()
        self.logger = Logger()
        self._workspace_module = None
        self._auth_module = None
        self._analytics_module = None
        self._forms_module = None
        self._submissions_module = None
        self._tasks_module = None
        self._communication_module = None
        self._document_module = None


    @property
    def workspace(self):
        if not self._workspace_module:
            self._workspace_module = Workspace(self.session, self.logger, self.base_url)
        return self._workspace_module
    
    @property
    def auth(self):
        if not self._workspace_module or not self._workspace_module.workspace_instance:
            raise Exception('Workspace not initialized! Please use workspace.init() before calling auth methods')
        if not self._auth_module:
            self._auth_module = Auth(self.session, self.logger, self.base_url, self._workspace_module.workspace_instance)
        return self._auth_module
    
    @property
    def analytics(self):
        
        self.validate()

        if not self._analytics_module:
            self._analytics_module = Analytics(self.session, self.logger, self.base_url)
        return self._analytics_module
    
    @property
    def forms(self):
        
        self.validate()

        if not self._forms_module:
            self._forms_module = Forms(self.session, self.logger, self.base_url)
        return self._forms_module
    
    @property
    def submissions(self):
        
        self.validate()

        if not self._submissions_module:
            self._submissions_module = Submissions(self.session, self.logger, self.base_url)
        return self._submissions_module
    
    @property
    def tasks(self):
        
        self.validate()

        if not self._tasks_module:
            self._tasks_module = Tasks(self.session, self.logger, self.base_url)
        return self._tasks_module

    @property
    def communication(self):

        self.validate()

        if not self._communication_module:
            self._communication_module = Communication(self.session, self.logger, self.base_url)
        return self._communication_module

    @property
    def document(self):

        self.validate()

        if not self._document_module:
            self._document_module = Document(self.session, self.logger, self.base_url)
        return self._document_module
    
    # Validate if workspace and user are initialized
    def validate(self):
        # Check if workspace is initialized 
        if self.workspace.workspace_instance is None:
            raise Exception('Workspace not initialized! Please use workspace.init() before calling auth methods')

        # Check if user is logged in
        if self.auth.user_instance is None:
            raise Exception('User not logged in! Please use auth.login() before calling *module methods')