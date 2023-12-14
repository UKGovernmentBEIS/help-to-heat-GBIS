import ast
from http import HTTPStatus
import logging

import requests
from django.conf import settings
from help_to_heat.frontdoor import interface

logger = logging.getLogger(__name__)


class EPCApi:
    def get_address_and_rrn(building, postcode):
        try:
            token = EPCApi.__get_access_token()
            return EPCApi.__try_get_address_and_rrn(token, building, postcode)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code
            if status_code == HTTPStatus.UNAUTHORIZED:
                try:
                    new_token = EPCApi.__update_access_token()
                    return EPCApi.__try_get_address_and_rrn(new_token, building, postcode)
                except:
                    logger.exception(f"Error making API request: {e}")
                    return None
            else:
                logger.exception(f"Error making API request: {e}")
                return None    
        

    def get_epc_details(rrn):
        try:
            token = EPCApi.__get_access_token()
            return EPCApi.__try_get_epc_details(token, rrn)
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code
            if status_code == HTTPStatus.UNAUTHORIZED:
                try:
                    new_token = EPCApi.__update_access_token()
                    return EPCApi.__try_get_epc_details(new_token, rrn)
                except:
                    logger.exception(f"Error making API request: {e}")
                    return None
            else:
                logger.exception(f"Error making API request: {e}")
                return None


    def __get_access_token():
        token = interface.api.session.retrieve_token()
        if token is not None:
            return token
        else:
            token = EPCApi.__update_access_token()
            return token


    def __update_access_token():
        client_id = settings.EPC_API_CLIENT_ID
        client_secret = settings.EPC_API_CLIENT_SECRET
        token_url = "https://api.epb-staging.digital.communities.gov.uk/auth/oauth/token"

        payload = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            access_token = response.json().get("access_token")
            interface.api.session.save_token(access_token)
            return access_token
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error fetching access token: {e}")
            return None

     
    def __try_get_address_and_rrn(token, building, postcode):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/assessments/domestic-epcs/search?postcode={postcode}&buildingNameOrNumber={building}"  # noqa E501
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data


    def __try_get_epc_details(token, rrn):
        url = f"https://api.epb-staging.digital.communities.gov.uk/api/ecoplus/assessments/{rrn}"
        headers = {"Authorization": f"Bearer {token}"}
    
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data