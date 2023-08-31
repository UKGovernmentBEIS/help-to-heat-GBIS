from help_to_heat.frontdoor.os_api import OSApi


def test_os_api_init():
    api_client = OSApi('["key1", "key2", "key3"]')
    assert api_client.keys == ["key1", "key2", "key3"]


def test_os_api_happy_path():
    mock_response = "mock response"

    class MockClient(OSApi):
        def perform_request(self, url):
            return mock_response

    api_client = MockClient('["key"]')
    response = api_client.get_by_postcode("w1a 1aa", 0, 100)
    assert response == mock_response


def test_os_api_no_result():
    mock_response = []

    class MockClient(OSApi):
        def perform_request(self, url):
            return mock_response

    api_client = MockClient('["key"]')
    response = api_client.get_by_postcode("postcode with no addresses", 0, 100)
    assert response == mock_response
