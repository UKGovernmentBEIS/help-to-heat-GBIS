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
                # we log the postcode here in case of error to help diagnose if there are patterns in the kinds of
                # postcodes that cause a ratelimit hit
                # surrounding logs will only contain the session ID and general flow throughout the site
                # so, it is not possible to attribute the postcode to any other details
                # the logs themselves are retained for a week in CloudWatch
                status_code = e.response.status_code
                if status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    logger.error(
                        f"The OS API usage limit has been hit for API key at index {index} for postcode {postcode}."
                    )
                    if index == len(self.keys) - 1:
                        logger.error(f"The OS API usage limit has been hit for all API keys for postcode {postcode}.")
                        raise ThrottledApiException
                    else:
                        continue

                logger.exception(f"An error occurred while attempting to fetch addresses for postcode {postcode}.")
                break
        return []

    def perform_request(self, url):
        response = requests.get(url, timeout=default_api_timeout)
        response.raise_for_status()
        json_response = response.json()

        return json_response
