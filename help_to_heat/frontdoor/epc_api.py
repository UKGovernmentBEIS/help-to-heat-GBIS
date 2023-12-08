import ast
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ThrottledApiException(Exception):
    pass


class EPCApi:
    def __init__(self, keys):
        self.keys = ast.literal_eval(keys)

    def get_access_token():
        client_id = settings.EPC_API_CLIENT_ID
        client_secret = settings.EPC_API_CLIENT_SECRET
        token_url = "https://api.epb-staging.digital.communities.gov.uk/auth/oauth/token"

        payload = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            access_token = response.json().get("access_token")
            return access_token
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error fetching access token: {e}")
            return None

    def get_address_and_rrn(token, building, postcode):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/assessments/domestic-epcs/search?postcode={postcode}&buildingNameOrNumber={building}"  # noqa E501
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error making API request: {e}")
            return None

    def get_epc_details(token, rrn):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/ecoplus/assessments/{rrn}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for 4XX and 5XX status codes
            data = response.json()
            # Process the response data
            return data
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error making API request: {e}")
            return None
