from ..modules.documents import Document

class Communication:
    def __init__(self, session, logger, base_url):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = None

    def sendMailToRoles(self, roles: list, subjectTemplateId: int, messageTemplateId: int, variables: dict, communicationType: str = "MAIL"):
        """
        Send mail to roles.

        :param roles: ["Role1, Role2, Role3, ...]
        :param subjectTemplateId: Template ID of custom document
        :param messageTemplateId: Template ID of custom document
        :param variables:
        :param communicationType:
        :return:
        """
        try:
            document = Document(self.session, self.logger, self.base_url)

            subject = document.getCustomTemplateData(subjectTemplateId, variables)
            message = document.getCustomTemplateData(messageTemplateId, variables)

            body = {}
            body['groupname'] = roles
            body['commtype'] = [communicationType]
            body['title'] = subject
            body['msg'] = message

            businessTag = dict(self.session.headers)["businessTagID"]
            url = f"{self.base_url}/rest/v13/usergroups/message/{businessTag}"
            response = self.session.post(url, json=body)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Email sent successfully.")
            else:
                raise ValueError(resp.get('message'))
            return resp
        except Exception as e:
            self.logger.error(e)
            raise e

    def sendMailToEmails(self, emails: list, subjectTemplateId: int, messageTemplateId: int, variables: dict, communicationType: str = "MAIL", cc=None, bcc=None, replyTo=None, attachments=None, userName=None, defaultFooter=False, verify=True):
        """
        Send mail to email addresses.

        :param emails: ["EmailId1", "EmailId2", ....]
        :param subjectTemplateId:
        :param messageTemplateId:
        :param variables:
        :param communicationType:
        :param cc:
        :param bcc:
        :param replyTo:
        :param attachments:
        :param userName:
        :param defaultFooter: True/False
        :param verify: For SSL verification (True/False)
        :return:
        """
        try:
            document = Document(self.session, self.logger, self.base_url)

            subject = document.getCustomTemplateData(subjectTemplateId, variables)
            message = document.getCustomTemplateData(messageTemplateId, variables)

            emails = ','.join(emails)
            businessTag = dict(self.session.headers)["businessTagID"]

            body = {
                "email": emails,
                "OrgName": businessTag,
                "subject": subject,
                "msg": message,
                "attachments": attachments,
                "defaultFooterHide": defaultFooter,
                "verify": verify
            }

            if cc:
                body['cc'] = cc
            if bcc:
                body['bcc'] = bcc
            if replyTo:
                body['replyTo'] = replyTo
            if userName:
                body["username"] = userName

            url = f"{self.base_url}/rest/v13/{businessTag}/send/email"
            response = self.session.post(url, json=body)
            response.raise_for_status()  # Raise an exception for HTTP errors

            resp = response.json()
            if resp.get('error') == False:
                self.logger.info(f"Email sent successfully.")
            else:
                raise ValueError(resp.get('message'))
            return resp
        except Exception as e:
            self.logger.error(e)
            raise e
