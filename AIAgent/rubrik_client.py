import requests
import urllib3

urllib3.disable_warnings()


class RubrikClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://unisys-demo.my.rubrik.com/api/client_token"
        self.graphql_url = "https://unisys-demo.my.rubrik.com/api/graphql"

    def get_access_token(self):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(
            self.token_url,
            json=payload,
            verify=False,
        )

        print("Token API Status:", response.status_code)
        response.raise_for_status()

        return response.json()["access_token"]

    def execute_query(self, query):
        token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.graphql_url,
            json={"query": query},
            headers=headers,
            verify=False,
        )

        print("GraphQL Status:", response.status_code)
        response.raise_for_status()

        return response.json()