import logging
from http import HTTPStatus

import requests

logger = logging.getLogger(__name__)


class ThrottledApiException(Exception):
    pass


class OSApi:
    def __init__(self, key):
        self.key = key

    def get_by_postcode(self, postcode, offset, max_results):
        url = f"""https://api.os.uk/search/places/v1/postcode?maxresults={max_results}
            &postcode={postcode}&lr=EN&dataset=DPA,LPI&key={self.key}"""
        if offset:
            url += f"&offset={offset}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            json_response = response.json()

            return json_response

        except requests.exceptions.HTTPError or requests.exceptions.RequestException as e:
            status_code = e.response.status_code
            if status_code == HTTPStatus.TOO_MANY_REQUESTS:
                logger.error("The OS API usage limit has been hit.")
                raise ThrottledApiException

            logger.error("An error occured while attempting to fetch addresses.")
            logger.error(e)

        return []
