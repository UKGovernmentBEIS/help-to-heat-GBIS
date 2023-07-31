import json
import logging
import pathlib

logger = logging.getLogger(__name__)

__here__ = pathlib.Path(__file__).parent
DATA_DIR = __here__ / "mock_os_api_data"


class MockOSApi:
    files = {"postcode": "sample_os_api_postcode_response.json", "uprn": "sample_os_api_uprn_response.json"}

    def __init__(self, key):
        self.key = key

    def get_by_postcode(self, postcode, offset, max_results):
        content = (DATA_DIR / self.files["postcode"]).read_text()
        return json.loads(content)

    def get_by_uprn(self, uprn, dataset):
        content = (DATA_DIR / self.files["uprn"]).read_text()
        return json.loads(content)


class EmptyOSApi(MockOSApi):
    files = {"postcode": "empty_osdatahub_response.json", "uprn": "empty_osdatahub_response.json"}
