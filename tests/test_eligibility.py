import datetime
import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.eligibility import calculate_eligibility
from help_to_heat.frontdoor.mock_os_api import MockOSApi
from help_to_heat.portal import models

from . import utils

result_map = {
    "GBIS": ("GBIS",),
    "ECO4": ("ECO4",),
    "NONE": (),
    "BOTH": ("GBIS", "ECO4"),
}

scenarios = (
    (
        {
            "benefits": "Yes",
            "epc_rating": "D",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "BOTH",
    ),
    (
        {
            "benefits": "Yes",
            "epc_rating": "G",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "BOTH",
    ),
    (
        {
            "benefits": "Yes",
            "epc_rating": "D",
            "country": "England",
            "own_property": "No, I am a social housing tenant",
        },
        "BOTH",
    ),
    (
        {
            "benefits": "Yes",
            "epc_rating": "E",
            "country": "England",
            "own_property": "No, I am a tenant",
        },
        "BOTH",
    ),
    (
        {
            "council_tax_band": "D",
            "benefits": "No",
            "epc_rating": "E",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "GBIS",
    ),
    (
        {
            "council_tax_band": "D",
            "benefits": "Yes",
            "epc_rating": "D",
            "country": "England",
            "own_property": "No, I am a tenant",
        },
        "GBIS",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "No",
            "epc_rating": "D",
            "country": "England",
        },
        "NONE",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "Yes",
            "epc_rating": "D",
            "country": "England",
            "own_property": "No, I am a tenant",
        },
        "GBIS",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "No",
            "country": "England",
        },
        "NONE",
    ),
)

unknown_epc_scenarios = (
    (
        {
            "council_tax_band": "B",
            "benefits": "Yes",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "BOTH",
    ),
    (
        {
            "council_tax_band": "G",
            "benefits": "Yes",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "BOTH",
    ),
    (
        {
            "council_tax_band": "D",
            "benefits": "No",
            "country": "England",
            "own_property": "Yes, I own my property and live in it",
        },
        "GBIS",
    ),
    (
        {
            "council_tax_band": "D",
            "benefits": "Yes",
            "country": "England",
            "own_property": "No, I am a tenant",
        },
        "BOTH",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "No",
            "country": "England",
        },
        "NONE",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "Yes",
            "country": "England",
            "own_property": "No, I am a tenant",
        },
        "BOTH",
    ),
    (
        {
            "council_tax_band": "F",
            "benefits": "No",
            "country": "England",
        },
        "NONE",
    ),
)


def test_eligibility():
    for data, expected in scenarios:
        result = calculate_eligibility(data)
        expected = result_map[expected]
        assert expected == result, (data, expected, result)


def test_eligibility_unknown_epc():
    for data, expected in unknown_epc_scenarios:
        result = calculate_eligibility(data)
        expected = result_map[expected]
        assert expected == result, (data, expected, result)


eligible_council_tax = {
    "England": {
        "eligible": ("A", "B", "C", "D"),
        "ineligible": ("E", "F", "G"),
    },
    # TODO Write Unit tests to properly test this logic
    # "Scotland": {
    #     "eligible": ("A", "B", "C", "D", "E"),
    #     "ineligible": ("F", "G"),
    # },
    "Wales": {
        "eligible": ("A", "B", "C", "D", "E"),
        "ineligible": ("F", "G"),
    },
}


def test_eco4_scenario_1():
    for country in eligible_council_tax:
        for own_property in ("Yes, I own my property and live in it",):
            for epc_rating in ("D", "E", "F", "G", "Not found"):
                for benefits in ("Yes",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "own_property": own_property,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["BOTH"]
                    assert result == expected


def test_eco4_scenario_2():
    for country in eligible_council_tax:
        for own_property in (
            "No, I am a tenant",
            "Yes, I am the property owner but I lease the property to one or more tenants",
        ):
            for epc_rating in ("E", "F", "G", "Not found"):
                for benefits in ("Yes",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "own_property": own_property,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["BOTH"]
                    assert result == expected


def test_eco4_scenario_3():
    for country in eligible_council_tax:
        for own_property in ("No, I am a social housing tenant",):
            for epc_rating in ("D", "E", "F", "G", "Not found"):
                for benefits in ("Yes",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "own_property": own_property,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["BOTH"]
                    assert result == expected


def test_mural_scenario_3():
    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["eligible"]:
            for epc_rating in ("D", "E", "F", "G"):
                for benefits in ("No",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "council_tax_band": council_tax_band,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["GBIS"]
                    assert result == expected

    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["eligible"]:
            for epc_rating in "D":
                for benefits in ("Yes",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "council_tax_band": council_tax_band,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["GBIS"]
                    assert result == expected


def test_mural_scenario_3_1():
    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["ineligible"]:
            for epc_rating in "D":
                for benefits in ("Yes",):
                    session_data = {
                        "epc_rating": epc_rating,
                        "council_tax_band": council_tax_band,
                        "country": country,
                        "benefits": benefits,
                    }
                    result = calculate_eligibility(session_data)
                    expected = result_map["GBIS"]
                    assert result == expected


def _add_epc(uprn, rating):
    models.EpcRating.objects.update_or_create(
        uprn=uprn, defaults={"rating": rating, "date": datetime.date(2022, 12, 25)}
    )
    assert interface.api.epc.get_epc(uprn, "England")


def _make_check_page(session_id):
    def _check_page(page, page_name, key, answer):
        form = page.get_form()
        form[key] = answer
        page = form.submit().follow()

        data = interface.api.session.get_answer(session_id, page_name=page_name)
        assert data[key] == answer
        return page

    return _check_page


@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_ineligible_shortcut():
    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["ineligible"]:
            for epc_rating in ("D", "E", "F", "G"):
                _do_test(country=country, council_tax_band=council_tax_band, epc_rating=epc_rating)


def _do_test(country, council_tax_band, epc_rating):
    _add_epc(uprn="100023336956", rating=epc_rating)

    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = country
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "10"
    form["postcode"] = "SW1A 2AA"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["building_name_or_number"] == "10"
    assert data["postcode"] == "SW1A 2AA"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", council_tax_band)

    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", "No")

    assert page.has_one("h1:contains('Your property is not eligible')"), (country, council_tax_band, epc_rating)
