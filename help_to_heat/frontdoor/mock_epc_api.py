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


class MockRecommendationsNotFoundEPCApi(MockEPCApi):
    def get_epc_recommendations(self, lmk_key):
        raise NotFoundRequestException()


class MockRecommendationsInternalServerErrorEPCApi(MockEPCApi):
    def get_epc_recommendations(self, lmk_key):
        raise InternalServerErrorRequestException()


class MockRecommendationsTransientInternalServerErrorEPCApi(MockEPCApi):
    number_of_calls = 0

    def get_epc_recommendations(self, lmk_key):
        self.number_of_calls += 1
        if self.number_of_calls <= 2:
            raise InternalServerErrorRequestException()

        return super().get_epc_recommendations(lmk_key)


def get_mock_epc_api_expecting_address_and_postcode(check_address, check_postcode):
    class MockEpcApiExpectingAddressAndPostcode(MockEPCApi):
        def search_epc_details(self, address, postcode):
            if address != check_address or postcode != check_postcode:
                raise NotFoundRequestException()
            else:
                return super().search_epc_details(address, postcode)

    return MockEpcApiExpectingAddressAndPostcode


class UnauthorizedRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.UNAUTHORIZED


class NotFoundRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.NOT_FOUND


class InternalServerErrorRequestException(requests.exceptions.RequestException):
    def __init__(self):
        self.response = requests.Response()
        self.response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
