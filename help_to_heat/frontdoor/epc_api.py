import logging
import urllib.parse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EPCApi:
    def __init__(self, token):
        self.token = token

    def get_access_token(self):
        client_id = settings.EPC_API_CLIENT_ID
        client_secret = settings.EPC_API_CLIENT_SECRET
        base_url = settings.EPC_API_BASE_URL
        token_url = f"{base_url}/auth/oauth/token"

        payload = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")

    def get_address_and_rrn(self, building, postcode):
        base_url = settings.EPC_API_BASE_URL
        params = urllib.parse.urlencode({"postcode": postcode, "buildingNameOrNumber": building})
        url = f"{base_url}/api/assessments/domestic-epcs/search?{params}"
        return self.__api_call(url)

    def get_epc_details(self, rrn):
        base_url = settings.EPC_API_BASE_URL
        rrn_for_path = urllib.parse.quote(rrn)
        url = f"{base_url}/api/ecoplus/assessments/{rrn_for_path}"
        return self.__api_call(url)

    def __api_call(self, url):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
