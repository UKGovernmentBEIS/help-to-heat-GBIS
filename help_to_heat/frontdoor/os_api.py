import ast
import logging
from http import HTTPStatus

import requests

from help_to_heat.utils import default_api_timeout

logger = logging.getLogger(__name__)


class ThrottledApiException(Exception):
    pass


class OSApi:
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
        response = requests.get(url, timeout=default_api_timeout)
        response.raise_for_status()
        json_response = response.json()

        return json_response
