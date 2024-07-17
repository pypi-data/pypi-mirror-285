import urllib.parse


class Document:
    def __init__(self, session, logger, base_url):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = None

    def getCustomTemplateData(self, id: int, variables: dict):
        """
        Get custom Template Data.

        :param id: Template ID of custom document
        :param variables:
        :return:
        """
        try:
            url = f"{self.base_url}/rest/v13/custom/documents/generate/{id}"
            response = self.session.post(url, json=variables)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Template data retrieved successfully for custom document {id}")
            else:
                raise ValueError(resp.get('message'))
            return resp["data"]
        except Exception as e:
            self.logger.error(e)
            raise e

    def getCustomTemplateHtml(self, id: int, variables: dict):
        """
        Get custom Template HTML.

        :param id: Template ID of custom document
        :param variables:
        :return:
        """
        try:
            url = f"{self.base_url}/rest/v13/custom/documents/generate/{id}"
            response = self.session.post(url, json=variables)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Template HTML retrieved successfully for custom document {id}")
            else:
                raise ValueError(resp.get('message'))
            return resp["html"]
        except Exception as e:
            self.logger.error(e)
            raise e

    def getCustomDocumentLink(self, id: int, variables: dict, filters: dict = None):
        """
        Generate PDF link using custom doc template.

        :param id: Template ID of custom document
        :param variables:
        :param filters: {
                "header_doc_id": Header_Custom_Document_ID,
                "footer":'"{0}"'.format("yes/no"),
                "style":'"{0}"'.format("yes/no"),
                "orientation":'"{0}"'.format("P/L"),    P=Portrait, L=Landscape
                "margin_left":1,
                "margin_right":2,
                "margin_top":2,
                "margin_bottom":2,
                "margin_header":0,
                "margin_footer":0,
                "UseLogoAsWatermark":False
            }
            NOTE: Only send the filters that you require. Parameters for footer, style and orientation needs to be sent in the above specified format.
        :return:
        """
        if filters is None:
            filters = {}
        try:
            if filters:
                filter_dict = filters
                # Encoding the filter dictionary into query parameters
                filter_params = urllib.parse.urlencode(filter_dict)
                url = f"{self.base_url}/rest/v13/custom/documents/link/{id}?{filter_params}"
            else:
                url = f"{self.base_url}/rest/v13/custom/documents/link/{id}"
            response = self.session.post(url, json=variables)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"PDF generated successfully for custom document {id}")
            else:
                raise ValueError(resp.get('message'))
            return resp["data"]["link"]
        except Exception as e:
            self.logger.error(e)
            raise e