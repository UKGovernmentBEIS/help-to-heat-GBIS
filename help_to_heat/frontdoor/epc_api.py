import logging
import urllib.parse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EPCApi:
    def _basic_auth_header(self):
        return {"Accept": "application/json", "Authorization": f"Basic {settings.OPEN_EPC_API_TOKEN}"}

    def get_address_and_lmk(self, building, postcode):
        base_url = settings.OPEN_EPC_API_BASE_URL
        params = urllib.parse.urlencode({"postcode": postcode, "address": building})
        url = f"{base_url}/search?{params}"
        return self.__api_call(url)

    def get_epc_details(self, lmk):
        base_url = settings.OPEN_EPC_API_BASE_URL
        lmk_for_path = urllib.parse.quote(lmk)
        url = f"{base_url}/certificate/{lmk_for_path}"
        return self.__api_call(url)

    def __api_call(self, url):
        headers = self._basic_auth_header()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
