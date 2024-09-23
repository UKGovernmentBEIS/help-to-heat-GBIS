import json
import logging
import pathlib
from http import HTTPStatus

import requests

logger = logging.getLogger(__name__)

__here__ = pathlib.Path(__file__).parent
DATA_DIR = __here__ / "mock_epc_api_data"


def load_test_reponse(file_name):
    content = (DATA_DIR / file_name).read_text()
    return json.loads(content)


class MockEPCApi:
    def get_address_and_lmk(self, building, postcode):
        return load_test_reponse("sample_address_and_lmk_response.json")

    def get_epc_details(self, rrn):
        return load_test_reponse("sample_epc_response.json")


class MockEPCApiWithEPCC:
    def get_address_and_lmk(self, building, postcode):
        return load_test_reponse("sample_address_and_lmk_response.json")

    def get_epc_details(self, rrn):
        return load_test_reponse("sample_epc_response_with_epc_c.json")


class MockUnauthorizedEPCApi(MockEPCApi):
    def get_address_and_lmk(self, building, postcode):
        raise UnauthorizedRequestException()

    def get_epc_details(self, rrn):
        raise UnauthorizedRequestException()


class MockNotFoundEPCApi(MockEPCApi):
    def get_address_and_lmk(self, building, postcode):
        raise NotFoundRequestException()

    def get_epc_details(self, rrn):
        raise NotFoundRequestException()


class UnauthorizedRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.UNAUTHORIZED


class NotFoundRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.NOT_FOUND
