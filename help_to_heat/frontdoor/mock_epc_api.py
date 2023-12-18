import json
import logging
import pathlib
import requests
from http import HTTPStatus

logger = logging.getLogger(__name__)

__here__ = pathlib.Path(__file__).parent
DATA_DIR = __here__ / "mock_epc_api_data"

class MockEPCApi:
    files = {"address_and_rrn": "sample_address_and_rrn_response.json", 
             "epc": "sample_epc_response.json",
             "access_token": "sample_token_response.json"}
    
    def __init__(self, token):
        self.token = token

    def get_address_and_rrn(self, building, postcode):
        content = (DATA_DIR / MockEPCApi.files["address_and_rrn"]).read_text()
        return json.loads(content)


    def get_epc_details(self, rrn):
        content = (DATA_DIR / MockEPCApi.files["epc"]).read_text()
        return json.loads(content)
    
    
    def get_access_token(self):
        content = (DATA_DIR / MockEPCApi.files["access_token"]).read_text()
        return json.loads(content)


class MockUnauthorizedEPCApi(MockEPCApi):
    def get_address_and_rrn(self, building, postcode):
        raise UnauthorizedRequestException()


    def get_epc_details(self, rrn):
        raise UnauthorizedRequestException()


class MockNotFoundEPCApi(MockEPCApi):
    def get_address_and_rrn(self, building, postcode):
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