from elasticsearch_dsl import Search as ESearch
from ..models.submission import Submission

class Submissions:
    def __init__(self, session, logger, base_url):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = None
    
    def get(self, id):
        """
        Get form submission details from id.

        :param id: FormSubmissionID/id of entry
        :return:
        """
        try:
            url = f"{self.base_url}/api/v1/submissions/{id}"
            response = self.session.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Form details retrieved successfully for id {id}")
            else:
                raise ValueError(resp.get('message'))
            return Submission(**resp['data']['elements'][0])
        except Exception as e:
            self.logger.error(e)
            raise e

    def search(self, formId: str, searchObj: ESearch):
        """Search submissions"""

        # Accept only elasticsearch-dsl Search object as searchObj
        if not isinstance(searchObj, ESearch):
            raise ValueError("searchObj field should be an instance of elasticsearch-dsl Search object")
        
        if not formId:
            raise ValueError("formId field is required to search the submissions")

        try:
            query = searchObj.to_dict()
            url = f"{self.base_url}/api/v1/analytics/search"
            response = self.session.post(url, json={'formId': formId, 'query': query})
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully completed search operation for form {id}")
            else:
                raise ValueError(resp.get('message'))
            return resp['data']
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def put(self, submission: Submission, skipValidation: bool = True, skipAutomation: bool = True, skipFormulaValidation: bool = True):
        """Update existing submission"""
        if not isinstance(submission, Submission):
            raise ValueError("submission field should be an instance of Submission model")

        if not submission.id:
            raise ValueError("id field is required to update the submission")
        
        if not submission.elements or submission.elements == []:
            raise ValueError("elements field with atleast 1 element is required to update the submission")

        try:
            url = f"{self.base_url}/api/v1/submissions/{submission.id}?skipValidation={skipValidation}&skipAutomation={skipAutomation}&skipFormulaValidation={skipFormulaValidation}"
            response = self.session.put(url, json=submission.model_dump(exclude_none=True, exclude_unset=True))
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully updated entry for id {submission.id}")
            else:
                raise ValueError(resp.get('message'))
            return resp
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def post(self, submission: Submission, skipValidation: bool = True, skipAutomation: bool = True, skipFormulaValidation: bool = True):
        """Create a new submission"""
        if not isinstance(submission, Submission):
            raise ValueError("submission field should be an instance of Submission model")

        if not submission.formId:
            raise ValueError("formId field is required to create the submission")
        
        if not submission.elements:
            raise ValueError("elements field is required to create the submission")

        try:
            url = f"{self.base_url}/api/v1/submissions?skipValidation={skipValidation}&skipAutomation={skipAutomation}&skipFormulaValidation={skipFormulaValidation}"
            response = self.session.post(url, json=submission.model_dump(exclude_none=True, exclude_unset=True))
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Successfully added a new entry for form {submission.formId}")
            else:
                raise ValueError(resp.get('message'))
            return resp
        except Exception as e:
            self.logger.error(e)
            raise e