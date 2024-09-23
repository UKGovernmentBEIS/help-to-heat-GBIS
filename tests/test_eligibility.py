import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.mock_epc_api import MockEPCApi

from . import utils

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


def _add_epc():
    assert interface.api.epc.get_address_and_epc_lmk("22", "FL23 4JA")
    assert interface.api.epc.get_epc_details("2222-2222-2222-2222-2222")


def _make_check_page(session_id):
    def _check_page(page, page_name, key, answer):
        form = page.get_form()
        form[key] = answer
        page = form.submit().follow()

        data = interface.api.session.get_answer(session_id, page_name=page_name)
        assert data[key] == answer
        return page

    return _check_page


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_ineligible_shortcut():
    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["ineligible"]:
            for epc_rating in ("D", "E", "F", "G"):
                _do_test(country=country, council_tax_band=council_tax_band, epc_rating=epc_rating)


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def _do_test(country, council_tax_band, epc_rating):
    _add_epc()

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
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form["lmk"] = "222222222222222222222222222222222"

    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc-select")
    assert data["lmk"] == "222222222222222222222222222222222"
    assert data["address"] == "22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", council_tax_band)
    data["epc_rating"] = epc_rating

    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", "No")

    page = _check_page(page, "household-income", "household_income", "£31,000 or more a year")

    assert page.has_one("h1:contains('Your property is not eligible')"), (country, council_tax_band, epc_rating)
