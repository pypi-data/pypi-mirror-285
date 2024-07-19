import requests
from .endpoints import Endpoints

class HeyTextualClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization: Bearer {api_key}"
        }
        self.endpoints = Endpoints()

    def extract(self, file_path, template_id):
        with open(file_path, 'rb') as file:
            response = requests.post(
                self.endpoints.extract,
                headers=self.headers,
                files={'archivo': file},
                data={'template': template_id}
            )
        return response.json()

    def documents(self, start_date=None, end_date=None, limit=None):
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "limit": limit
        }
        response = requests.post(
            self.endpoints.documents,
            headers=self.headers,
            data=params
        )
        return response.json()

    def document(self, document_id):
        response = requests.post(
            f"{self.endpoints.document}/{document_id}",
            headers=self.headers,
            data={'documentId': document_id}
        )
        return response.json()

    def templates(self, start_date=None, end_date=None, limit=None):
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "limit": limit
        }
        response = requests.post(
            self.endpoints.templates,
            headers=self.headers,
            data=params
        )
        return response.json()
