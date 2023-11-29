import ast
import logging
from http import HTTPStatus

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ThrottledApiException(Exception):
    pass


class EPCApi:
    def __init__(self, keys):
        self.keys = ast.literal_eval(keys)

    def get_by_postcode(self, postcode, offset, max_results):
        for index, key in enumerate(self.keys):
            url = f"""https://api.os.uk/search/places/v1/postcode?maxresults={max_results}
                &postcode={postcode}&lr=EN&dataset=DPA,LPI&key={key}"""
            if offset:
                url += f"&offset={offset}"

            try:
                return self.perform_request(url)

            except requests.exceptions.HTTPError or requests.exceptions.RequestException as e:
                status_code = e.response.status_code
                if status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    logger.error(f"The OS API usage limit has been hit for API key at index {index}.")
                    if index == len(self.keys) - 1:
                        logger.error("The OS API usage limit has been hit for all API keys")
                        raise ThrottledApiException
                    else:
                        continue

                logger.exception("An error occurred while attempting to fetch addresses.")
                break
        return []

    def perform_request(self, url):
        response = requests.get(url)
        response.raise_for_status()
        json_response = response.json()

        return json_response

    
    def get_access_token():
        client_id = settings.EPC_API_CLIENT_ID
        client_secret = settings.EPC_API_CLIENT_SECRET
        token_url = 'https://api.epb-staging.digital.communities.gov.uk/auth/oauth/token' 

        # Define payload for token request (for Client Credentials Grant Type)
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()  # Raise an error for 4XX and 5XX status codes
            access_token = response.json().get('access_token')
            print(access_token)
            return access_token
        except requests.exceptions.RequestException as e:
            print('Error fetching access token:', e)
            return None
      
    
    def get_address_and_rrn(token, building, postcode):
        url = f'https://api.epb-staging.digital.communities.gov.uk/api/assessments/domestic-epcs/search?postcode={postcode}&buildingNameOrNumber={building}'
        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for 4XX and 5XX status codes
            data = response.json()
            # Process the response data
            print(data)
            return data
        except requests.exceptions.RequestException as e:
            print('Error making API request:', e)
            return None
    
    def get_epc_details(token, rrn):
        url = f'https://api.epb-staging.digital.communities.gov.uk/api/ecoplus/assessments/{rrn}'
        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for 4XX and 5XX status codes
            data = response.json()
            # Process the response data
            print(data)
            return data
        except requests.exceptions.RequestException as e:
            print('Error making API request:', e)
            return None

