import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EPCApi:
    def __init__(self, token):
        self.token = token

    def get_access_token(self):
        client_id = settings.EPC_API_CLIENT_ID
        client_secret = settings.EPC_API_CLIENT_SECRET
        token_url = "https://api.epb-staging.digital.communities.gov.uk/auth/oauth/token"

        payload = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")

    def get_address_and_rrn(self, building, postcode):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/assessments/domestic-epcs/search?postcode={postcode}&buildingNameOrNumber={building}"  # noqa E501
        return self.__api_call(url)

    def get_epc_details(self, rrn):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/ecoplus/assessments/{rrn}"
        return self.__api_call(url)

    def __api_call(self, url):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
