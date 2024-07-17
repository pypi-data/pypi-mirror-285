from elasticsearch_dsl import Search as ESearch
from ..models.task import Task

class Tasks:
    def __init__(self, session, logger, base_url):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = None
    
    def get(self, id):
        """
        Get form details from id

        :param id:
        :return:
        """
        try:
            url = f"{self.base_url}/api/v1/tasks/{id}"
            response = self.session.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully fetched task for task {id}")
            else:
                raise ValueError(resp.get('message'))
            return Task(**resp['data']['elements'][0])
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def search(self, searchObj: ESearch):
        """
        Search tasks

        :param searchObj:
        :return:
        """
        # Accept only elasticsearch-dsl Search object as searchObj
        if not isinstance(searchObj, ESearch):
            raise ValueError("searchObj field should be an instance of elasticsearch-dsl Search object")

        try:
            query = searchObj.to_dict()
            url = f"{self.base_url}/api/v1/analytics/search"
            response = self.session.post(url, json={'isTask': True, 'query': query})
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully completed search operation for task.")
            else:
                raise ValueError(resp.get('message'))
            return resp['data']
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def put(self, task: Task):
        """
        Update existing task

        :param task:
        :return:
        """
        # task should be a valid Task model
        if not isinstance(task, Task):
            raise ValueError("task field should be an instance of Task model")
        # id or uuid field is required in the task model to update the task
        if not task.id and not task.uuid:
            raise ValueError("id or uuid field is required to update the task")

        try:
            url = f"{self.base_url}/api/v1/tasks"
            response = self.session.put(url, json=task.model_dump(exclude_none=True, exclude_unset=True))
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully updated task for id {task.id}")
            else:
                raise ValueError(resp.get('message'))
            return resp['data']
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def post(self, task: Task):
        """
        Create a new task

        :param task:
        :return:
        """
        if not isinstance(task, Task):
            raise ValueError("task field should be an instance of Task model")

        try:
            url = f"{self.base_url}/api/v1/tasks"
            response = self.session.post(url, json=task.model_dump(exclude_none=True, exclude_unset=True))
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully added a new entry for form {task.title}")
            else:
                raise ValueError(resp.get('message'))
            return resp["data"]
        except Exception as e:
            self.logger.error(e)
            raise e