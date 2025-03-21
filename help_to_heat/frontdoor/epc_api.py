import logging
import urllib.parse

import requests
from django.conf import settings

from help_to_heat.utils import default_api_timeout

logger = logging.getLogger(__name__)


class EPCApi:
    def _basic_auth_header(self):
        return {"Accept": "application/json", "Authorization": f"Basic {settings.OPEN_EPC_API_TOKEN}"}

    # see help_to_heat/frontdoor/mock_epc_api_data/sample_search_response.json for example format
    def search_epc_details(self, building, postcode):
        params = urllib.parse.urlencode({"postcode": postcode, "address": building})
        url = f"{settings.OPEN_EPC_API_BASE_URL}/search?{params}"
        return self.__api_call(url)

    # see help_to_heat/frontdoor/mock_epc_api_data/sample_epc_response.json for example format
    def get_epc_details(self, lmk):
        lmk_for_path = urllib.parse.quote(lmk)
        url = f"{settings.OPEN_EPC_API_BASE_URL}/certificate/{lmk_for_path}"
        return self.__api_call(url)

    # see help_to_heat/frontdoor/mock_epc_api_data/sample_epc_recommendations_response.json for example format
    def get_epc_recommendations(self, lmk):
        lmk_for_path = urllib.parse.quote(lmk)
        url = f"{settings.OPEN_EPC_API_BASE_URL}/recommendations/{lmk_for_path}"
        return self.__api_call(url)

    def __api_call(self, url):
        headers = self._basic_auth_header()
        response = requests.get(url, headers=headers, timeout=default_api_timeout)
        response.raise_for_status()
        if len(response.content) == 0:
            return None
        return response.json()
