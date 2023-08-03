import datetime
import random
import string
import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.portal import models
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


def test_get_epc():
    uprn = str(int("".join(random.choices(string.digits, k=5))))
    data = {
        "uprn": uprn,
        "rating": "A",
        "date": datetime.date(2020, 12, 25),
    }
    models.EpcRating.objects.create(**data)

    found_epc = interface.api.epc.get_epc(uprn, "England")
    assert found_epc["rating"] == data["rating"]

    new_uprn = "".join(random.choices(string.digits, k=5))
    missing_epc = interface.api.epc.get_epc(new_uprn, "England")
    assert missing_epc == {}
