import logging
from http import HTTPStatus

import requests
import ast

logger = logging.getLogger(__name__)


class ThrottledApiException(Exception):
    pass


class OSApi:
    def __init__(self, keys):
        self.keys = ast.literal_eval(keys)
        self.key_index = 0

    def get_by_postcode(self, postcode, offset, max_results):
        new_key_available = True

        while new_key_available:
            url = f"""https://api.os.uk/search/places/v1/postcode?maxresults={max_results}
                &postcode={postcode}&lr=EN&dataset=DPA,LPI&key={self.keys[self.key_index]}"""
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
                    logger.error(f"The OS API usage limit has been hit for API key at index {self.key_index}.")

                    if not new_key_available:
                        logger.error("The OS API usage limit has been hit for all API keys.")
                        raise ThrottledApiException
                    else:
                        if self.key_index == len(self.keys)-1:
                            raise ThrottledApiException
                        else:
                            self.key_index += 1
                            continue

                logger.error("An error occured while attempting to fetch addresses.")
                logger.error(e)
                break


        return []
