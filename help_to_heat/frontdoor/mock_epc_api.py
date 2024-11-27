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
    def search_epc_details(self, building, postcode):
        return load_test_reponse("sample_search_response.json")

    def get_epc_details(self, rrn):
        return load_test_reponse("sample_epc_response.json")

    def get_epc_recommendations(self, lmk_key):
        return load_test_reponse("sample_epc_recommendations_response.json")


class MockEPCApiWithOldEPC(MockEPCApi):
    def search_epc_details(self, building, postcode):
        return load_test_reponse("sample_search_response_with_old_epc.json")


class MockEPCApiWithEPCC(MockEPCApi):
    def get_epc_details(self, rrn):
        epc = load_test_reponse("sample_epc_response.json")
        epc["rows"][0]["current-energy-rating"] = "C"
        return epc


class MockUnauthorizedEPCApi(MockEPCApi):
    def search_epc_details(self, building, postcode):
        raise UnauthorizedRequestException()

    def get_epc_details(self, rrn):
        raise UnauthorizedRequestException()

    def get_epc_recommendations(self, lmk_key):
        raise UnauthorizedRequestException()


class MockNotFoundEPCApi(MockEPCApi):
    def search_epc_details(self, building, postcode):
        raise NotFoundRequestException()

    def get_epc_details(self, rrn):
        raise NotFoundRequestException()

    def get_epc_recommendations(self, lmk_key):
        raise NotFoundRequestException()


class UnauthorizedRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.UNAUTHORIZED


class NotFoundRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.NOT_FOUND
