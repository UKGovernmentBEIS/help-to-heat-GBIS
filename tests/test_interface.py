import unittest
import uuid
from http import HTTPStatus

import requests

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.mock_epc_api import (
    MockEPCApi,
    MockNotFoundEPCApi,
    MockUnauthorizedEPCApi,
)
from help_to_heat.frontdoor.mock_os_api import MockOSApi

from . import utils


def test_answers():
    session_id = uuid.uuid4()
    page_name = "country"
    data = {"floob": "blumble", "country": "England"}
    result = interface.api.session.save_answer(session_id=session_id, page_name=page_name, data=data)
    expected = {"country": "England"}
    assert result == expected, (result, expected)

    result = interface.api.session.get_answer(session_id=session_id, page_name=page_name)
    assert result == expected, (result, expected)


def test_answer_missing():
    session_id = uuid.uuid4()
    page_name = "country"
    expected = {}
    result = interface.api.session.get_answer(session_id=session_id, page_name=page_name)
    assert result == expected, (result, expected)


def test_duplicate_answer():
    session_id = uuid.uuid4()
    page_name = "country"
    data = {"floob": "blumble", "country": "England"}
    result = interface.api.session.save_answer(session_id=session_id, page_name=page_name, data=data)
    expected = {"country": "England"}
    assert result == expected, (result, expected)

    data = {"floob": "blumble", "country": "Wales"}
    result = interface.api.session.save_answer(session_id=session_id, page_name=page_name, data=data)
    expected = {"country": "Wales"}
    assert result == expected, (result, expected)

    result = interface.api.session.get_answer(session_id=session_id, page_name=page_name)
    assert result == expected, (result, expected)


@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
def test_find_addresses():
    result = interface.api.address.find_addresses("10", "sw1a 2aa")
    assert result[0]["uprn"] == "100023336956"


@utils.mock_os_api
def test_get_address():
    result = interface.api.address.get_address(uprn="10")
    assert result["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_get_epc():
    assert interface.api.epc.get_address_and_epc_rrn("22", "FL23 4JA")
    found_epc = interface.api.epc.get_epc_details("1111-1111-1111-1111-1111")
    assert found_epc["data"]["assessment"].get("currentEnergyEfficiencyBand").upper() == "E"


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@utils.mock_os_api
def test_get_epc_not_found_failure():
    try:
        interface.api.epc.get_address_and_epc_rrn("10", "SW1A 2AA")
        raise "Expected call to throw"
    except requests.exceptions.RequestException as e:
        assert e.response.status_code == HTTPStatus.NOT_FOUND


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockUnauthorizedEPCApi)
@utils.mock_os_api
def test_get_epc_unauthorized_failure():
    try:
        interface.api.epc.get_address_and_epc_rrn("10", "SW1A 2AA")
        raise "Expected call to throw"
    except requests.exceptions.RequestException as e:
        assert e.response.status_code == HTTPStatus.UNAUTHORIZED


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@utils.mock_os_api
def test_get_epc_details_not_found_failure():
    try:
        interface.api.epc.get_epc_details("1111-1111-1111-1111-1111")
        raise "Expected call to throw"
    except requests.exceptions.RequestException as e:
        assert e.response.status_code == HTTPStatus.NOT_FOUND


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockUnauthorizedEPCApi)
@utils.mock_os_api
def test_get_epc_details_unauthorized_failure():
    try:
        interface.api.epc.get_epc_details("1111-1111-1111-1111-1111")
        raise "Expected call to throw"
    except requests.exceptions.RequestException as e:
        assert e.response.status_code == HTTPStatus.UNAUTHORIZED
