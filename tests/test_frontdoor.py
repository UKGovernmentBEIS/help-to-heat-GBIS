import unittest
import uuid

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.consts import (
    address_all_address_and_details_field,
    address_building_name_or_number_field,
    address_page,
    address_postcode_field,
    alternative_supplier_field,
    country_field,
    country_page,
    lmk_field,
    recommendations_field,
    supplier_field,
    supplier_field_eon_next,
    supplier_field_not_listed,
    supplier_field_utilita,
    supplier_field_utility_warehouse,
    user_selected_supplier_field,
)
from help_to_heat.frontdoor.mock_epc_api import (
    MockEPCApi,
    MockEPCApiWithEPCC,
    MockEPCApiWithMultipleEPC,
    MockNotFoundEPCApi,
    MockRecommendationsInternalServerErrorEPCApi,
    MockRecommendationsNotFoundEPCApi,
    MockRecommendationsTransientInternalServerErrorEPCApi,
    get_mock_epc_api_expecting_address_and_postcode,
)
from help_to_heat.frontdoor.mock_os_api import EmptyOSApi, MockOSApi
from help_to_heat.portal import models

from . import utils

# TODO: PC-380: Add tests for cookie banner


def test_start_page_redirection():
    client = utils.get_client()
    page = client.get("/start")

    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    page_name = page.path.split("/")[2]
    assert page_name == "country"


def test_flow_northern_ireland():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    form["country"] = "Northern Ireland"
    page = form.submit().follow()

    assert page.has_text("This service is not available for homes in Northern Ireland")

    data = interface.api.session.get_answer(session_id, page_name="country")
    assert data["country"] == "Northern Ireland"

    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Where is the property located?')")

    data = interface.api.session.get_answer(session_id, page_name="northern-ireland")
    assert data["_page_name"] == "northern-ireland", data


def test_flow_errors():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    page = form.submit()

    assert page.has_one("h2:contains('There is a problem')")
    assert page.has_text("Select where the property is located")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def _answer_house_questions(
    page,
    session_id,
    benefits_answer,
    supplier="Utilita",
    use_alternative=False,
    park_home=False,
    has_loft=True,
    household_income="Less than £31,000 a year",
):
    """Answer main flow with set answers"""

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    if not use_alternative:
        form = page.get_form()
        form["supplier"] = supplier
        page = form.submit().follow()
    else:
        form = page.get_form()
        form["supplier"] = supplier_field_not_listed
        page = form.submit().follow()

        assert page.has_text("Select an alternative energy supplier")
        form = page.get_form()
        form[alternative_supplier_field] = supplier
        page = form.submit().follow()

    if supplier == "Bulb, now part of Octopus Energy":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to Octopus Energy")
        page = form.submit().follow()
    if supplier == "Utility Warehouse":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to E.ON Next")
        page = form.submit().follow()
    if supplier == "Shell":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to Octopus Energy")
        page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No" if not park_home else "Yes")

    if park_home:
        assert page.has_text("Is the park home your main residence?")
        page = _check_page(page, "park-home-main-residence", "park_home_main_residence", "Yes")

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

    if not park_home:
        assert page.has_one("h1:contains('What is the council tax band of your property?')")
        page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", benefits_answer)

    if benefits_answer == "No":
        assert page.has_one("h1:contains('What is your annual household income?')")
        page = _check_page(page, "household-income", "household_income", household_income)

    if not park_home:
        assert page.has_one("h1:contains('What kind of property do you have?')")
        page = _check_page(page, "property-type", "property_type", "House")

        assert page.has_one("h1:contains('What kind of house do you have?')")
        page = _check_page(page, "property-subtype", "property_subtype", "Detached")

        assert page.has_one("h1:contains('How many bedrooms does the property have?')")
        page = _check_page(page, "number-of-bedrooms", "number_of_bedrooms", "Two bedrooms")

        assert page.has_one("h1:contains('What kind of walls does your property have?')")
        page = _check_page(page, "wall-type", "wall_type", "Cavity walls")

        assert page.has_one("h1:contains('Are your walls insulated?')")
        page = _check_page(page, "wall-insulation", "wall_insulation", "No they are not insulated")

        assert page.has_one("""h1:contains("Do you have a loft that has not been converted into a room?")""")
        if has_loft:
            page = _check_page(page, "loft", "loft", "Yes, I have a loft that has not been converted into a room")

            assert page.has_one("h1:contains('Is there access to your loft?')")
            page = _check_page(page, "loft-access", "loft_access", "Yes, there is access to my loft")

            assert page.has_one("h1:contains('How much loft insulation do you have?')")
            page = _check_page(
                page, "loft-insulation", "loft_insulation", "I have less than or equal to 100mm of loft insulation"
            )
        else:
            page = _check_page(
                page, "loft", "loft", "No, I do not have a loft or my loft has been converted into a room"
            )

    assert page.has_one("h1:contains('Check your answers')")
    form = page.get_form()
    page = form.submit().follow()

    return page


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_happy_flow():
    supplier = "Utilita"
    session_id, _ = _do_happy_flow(supplier=supplier)

    data = interface.api.session.get_answer(session_id, page_name="contact-details")
    expected = {
        "first_name": "Freddy",
        "last_name": "Flibble",
        "contact_number": "07777777777",
        "email": "freddy.flibble@example.com",
    }
    assert data == expected, (data, expected)

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == supplier
    assert referral.data["first_name"] == "Freddy"
    assert referral.data["benefits"] == "Yes"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def _do_happy_flow(
    supplier="EON",
    use_alternative=False,
    benefits_answer="Yes",
    park_home=False,
    household_income="Less than £31,000 a year",
):
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(
        page,
        session_id,
        benefits_answer=benefits_answer,
        supplier=supplier,
        use_alternative=use_alternative,
        park_home=park_home,
        household_income=household_income,
    )

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    if park_home or (benefits_answer == "No" and household_income == "£31,000 or more a year"):
        form["contribution_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    form["last_name"] = "Flimble"

    page = form.submit()
    assert page.has_text("Enter your first name")
    assert page.has_one("p#question-first_name-error.govuk-error-message:contains('Enter your first name')")
    form = page.get_form()
    assert form["last_name"] == "Flimble"

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = "07777777777"
    form["email"] = "freddy.flibble@example.com"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Confirm and submit')")

    form = page.get_form()
    page = form.submit()

    assert page.has_text("Please confirm that you agree to the use of your information by checking this box")
    form = page.get_form()
    form["permission"] = True
    form["acknowledge"] = True

    page = form.submit().follow()

    supplier_shown = supplier
    if supplier == "Bulb, now part of Octopus Energy":
        supplier_shown = "Octopus Energy"
    if supplier == "Utility Warehouse":
        supplier_shown = "E.ON Next"
    if supplier == "Shell":
        supplier_shown = "Octopus Energy"
    assert page.has_one(f"h1:contains('Your details have been submitted to {supplier_shown}')")

    return session_id, page


def _make_check_page(session_id):
    def _check_page(page, page_name, key, answer):
        form = page.get_form()
        form[key] = answer
        page = form.submit().follow()

        data = interface.api.session.get_answer(session_id, page_name=page_name)
        assert data[key] == answer
        return page

    return _check_page


def _get_change_button_for_chosen_page(page, page_name):
    # park home change link is an exception which is not followed by /change/
    filter_link = f"/{page_name}" if page_name == "park-home" else f"/{page_name}/change/"

    elements = page.all("a:contains('Change')")
    change = next(filter(lambda el: filter_link in el.attrib["href"], elements), None)
    return change


def _click_change_button(page, page_name):
    client = utils.get_client()
    change = _get_change_button_for_chosen_page(page, page_name)
    assert change is not None
    url = change.attrib["href"]
    return client.get(url)


def _assert_change_button_is_hidden(page, page_name):
    change = _get_change_button_for_chosen_page(page, page_name)
    assert change is None


def _assert_change_button_is_not_hidden(page, page_name):
    change = _get_change_button_for_chosen_page(page, page_name)
    assert change is not None


def test_back_button():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    assert page.has_one("h1:contains('Where is the property located?')")
    assert page.has_one("a:contains('Back')")

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("your home energy supplier from the list below")

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")

    form = page.get_form()
    form["own_property"] = "Yes, I own my property and live in it"
    page = form.submit().follow()

    page = page.click(contains="Back")

    form = page.get_form()
    assert form["own_property"] == "Yes, I own my property and live in it"

    page = page.click(contains="Back")

    form = page.get_form()
    assert form["supplier"] == "Utilita"

    page = page.click(contains="Back")

    form = page.get_form()
    assert form["country"] == "England"


@pytest.mark.parametrize(
    ("supplier_name", "expected_text"),
    [
        ("Shell", "Shell is now owned by Octopus Energy."),
        ("Bulb, now part of Octopus Energy", "Bulb is now owned by Octopus Energy."),
        ("Utility Warehouse", "Referral requests from UW customers will be managed by E.ON Next"),
    ],
)
def test_own_property_back_button_with_supplier_should_return_to_supplier_warning_page(supplier_name, expected_text):
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    page = _check_page(page, "country", "country", "England")

    page = _check_page(page, "supplier", "supplier", supplier_name)

    form = page.get_form()
    assert page.has_text(expected_text)
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")

    page = page.click(contains="Back")

    assert page.has_text(expected_text)


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_benefits_back_button_with_park_home_and_no_epc_should_return_to_address_select_page():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "Yes")

    assert page.has_text("Is the park home your main residence?")
    page = _check_page(page, "park-home-main-residence", "park_home_main_residence", "Yes")

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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")

    page = page.click(contains="Back")

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")

    page = page.click(contains="Back")

    assert page.has_one('h1:contains("Select your address")')


@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_benefits_back_button_with_park_home_and_scotland_should_return_to_address_select_page():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "Yes")

    assert page.has_text("Is the park home your main residence?")
    page = _check_page(page, "park-home-main-residence", "park_home_main_residence", "Yes")

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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")

    page = page.click(contains="Back")

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")

    page = page.click(contains="Back")

    assert page.has_one('h1:contains("Select your address")')


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_property_type_back_button_with_social_housing_and_no_epc_should_return_to_address_select_page():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "No, I am a social housing tenant")

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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('What kind of property do you have?')")

    page = page.click(contains="Back")

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")

    page = page.click(contains="Back")

    assert page.has_one('h1:contains("Select your address")')


@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_property_type_back_button_with_social_housing_and_scotland_should_return_to_address_select_page():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "No, I am a social housing tenant")

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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('What kind of property do you have?')")

    page = page.click(contains="Back")

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")

    page = page.click(contains="Back")

    assert page.has_one('h1:contains("Select your address")')


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApiWithEPCC)
def test_no_benefits_flow():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
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
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")
    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")

    form = page.get_form()
    form["accept_suggested_epc"] = "Yes"
    page = form.submit().follow()

    assert page.has_one("""h1:contains("It's likely that your home already has suitable energy saving measures")""")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_summary():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    page = page.click(contains="Back")

    page = page.click(contains="Change Do you own the property?")

    form = page.get_form()
    form["own_property"] = "Yes, I am the property owner but I lease the property to one or more tenants"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Check your answers')")

    assert page.has_text("Yes, I am the property owner but I lease the property to one or more tenants")
    assert page.has_text("22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", EmptyOSApi)
def test_no_address():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    assert page.has_one("h1:contains('Where is the property located?')")
    assert page.has_one("a:contains('Back')")

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("your home energy supplier from the list below")

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")

    form = page.get_form()
    form["own_property"] = "Yes, I own my property and live in it"
    page = form.submit().follow()

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    assert page.has_one("h2:contains('We could not find your address')")
    form = page.get_form()
    assert form["postcode"] == "FL23 4JA"
    form["address_line_1"] = "22 Acacia Avenue"

    page = form.submit()
    assert page.has_one("h2:contains('There is a problem')")
    assert page.has_text("Enter your Town or city")

    form = page.get_form()
    assert form["address_line_1"] == "22 Acacia Avenue"
    assert form["postcode"] == "FL23 4JA"

    form["address_line_2"] = "Smalltown"
    form["town_or_city"] = "Metropolis"
    form["county"] = "Big County"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-manual")
    assert data["address_line_1"] == "22 Acacia Avenue"
    assert data["town_or_city"] == "Metropolis"
    assert data["address_line_2"] == "Smalltown"
    assert data["town_or_city"] == "Metropolis"
    assert data["county"] == "Big County"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_epc_lookup_failure():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)
    supplier = "Utilita"

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = supplier
    page = form.submit().follow()

    if supplier == "Bulb, now part of Octopus Energy":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to Octopus Energy")
        page = form.submit().follow()
    if supplier == "Utility Warehouse":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to E.ON Next")
        page = form.submit().follow()
    if supplier == "Shell":
        form = page.get_form()
        assert page.has_text("Your referral will be sent to Octopus Energy")
        page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We could not find an Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")
    page = _check_page(page, "benefits", "benefits", "Yes")

    assert page.has_one("h1:contains('What kind of property do you have?')")
    page = _check_page(page, "property-type", "property_type", "House")

    assert page.has_one("h1:contains('What kind of house do you have?')")
    page = _check_page(page, "property-subtype", "property_subtype", "Detached")

    assert page.has_one("h1:contains('How many bedrooms does the property have?')")
    page = _check_page(page, "number-of-bedrooms", "number_of_bedrooms", "Two bedrooms")

    assert page.has_one("h1:contains('What kind of walls does your property have?')")
    page = _check_page(page, "wall-type", "wall_type", "Cavity walls")

    assert page.has_one("h1:contains('Are your walls insulated?')")
    page = _check_page(page, "wall-insulation", "wall_insulation", "No they are not insulated")

    assert page.has_one("""h1:contains("Do you have a loft that has not been converted into a room?")""")
    page = _check_page(page, "loft", "loft", "Yes, I have a loft that has not been converted into a room")

    assert page.has_one("h1:contains('Is there access to your loft?')")
    page = _check_page(page, "loft-access", "loft_access", "Yes, there is access to my loft")

    assert page.has_one("h1:contains('How much loft insulation do you have?')")
    page = _check_page(
        page, "loft-insulation", "loft_insulation", "I have less than or equal to 100mm of loft insulation"
    )

    assert page.has_one("h1:contains('Check your answers')")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = "07777777777"
    form["email"] = "freddy.flibble@example.com"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="contact-details")
    expected = {
        "first_name": "Freddy",
        "last_name": "Flibble",
        "contact_number": "07777777777",
        "email": "freddy.flibble@example.com",
    }
    assert data == expected, (data, expected)

    assert page.has_one("h1:contains('Confirm and submit')")
    form = page.get_form()
    form["permission"] = True
    form["acknowledge"] = True

    page = form.submit().follow()

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == supplier
    assert referral.data["first_name"] == "Freddy"
    assert referral.data["benefits"] == "Yes"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_eligibility():
    client = utils.get_client()
    page = client.get("/start")

    council_tax_band = "G"

    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
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

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "No")

    page = _check_page(page, "benefits", "benefits", "No")

    page = _check_page(page, "household-income", "household_income", "£31,000 or more a year")

    assert page.has_one("h1:contains('Your property is not eligible')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_schemes_page_logic_when_user_is_eligible_for_park_home_insulation_displays_park_home_insulation():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", park_home=True)

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert page.has_text("park home insulation")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    form["contribution_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_schemes_page_logic_when_user_may_contribute_checkbox_appears_and_is_required():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="No", household_income="£31,000 or more a year")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit()

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("There is a problem")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    form["contribution_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_schemes_page_logic_if_user_has_park_home_checkboxes_required():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="No", park_home=True)

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert page.has_text("park home insulation")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit()

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("There is a problem")
    assert page.has_text(
        "Please confirm that you understand your home must be sufficiently ventilated before any insulation is "
        "installed"
    )
    assert page.has_text(
        "Please confirm that you understand you may be required to contribute towards the cost of installing insulation"
    )
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    form["contribution_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_schemes_page_logic_if_user_may_have_to_contribute_checkboxes_required():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="No", household_income="£31,000 or more a year")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit()

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("There is a problem")
    assert page.has_text(
        "Please confirm that you understand your home must be sufficiently ventilated before any insulation is "
        "installed"
    )
    assert page.has_text(
        "Please confirm that you understand you may be required to contribute towards the cost of installing insulation"
    )
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    form["contribution_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_referral_email():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    page = form.submit()
    assert page.has_text("Enter your first name")
    assert page.has_one("p#question-first_name-error.govuk-error-message:contains('Enter your first name')")

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = "07777777777"
    form["email"] = "freddy.flibble@example.com"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Confirm and submit')")
    assert page.has_text("I agree for my personal details to be shared with Utilita")

    form = page.get_form()
    page = form.submit()

    assert page.has_text("Please confirm that you agree to the use of your information by checking this box")
    form = page.get_form()
    form["permission"] = True
    form["acknowledge"] = True

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")

    assert "Your details have been submitted to Utilita." in referral_email_text
    assert "You do not need to create another referral." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()


def test_feedback():
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()
    page = page.click(contains="feedback")
    assert (
        "https://forms.office.com/Pages/ResponsePage.aspx?id=BXCsy8EC60O0l-ZJLRst2JbIaLaL_"
        "oJOivXjaXYvCetUMFRBRVcyWkk4TzhYU0E4NjQzWlZMWThRMC4u" in page.url
    )


def test_accessibility_statement_with_session():
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Do you own the property?')")

    page = page.click(contains="Accessibility Statement")

    privacy_policy_session_id = page.path.split("/")[2]
    assert uuid.UUID(privacy_policy_session_id)

    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Do you own the property?')")


def test_accessibility_statement_then_privacy_policy_with_session():
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Do you own the property?')")

    page = page.click(contains="Accessibility Statement")
    page = page.click(contains="Privacy Policy")

    privacy_policy_session_id = page.path.split("/")[2]
    assert uuid.UUID(privacy_policy_session_id)

    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Do you own the property?')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_incorrect_referral_email():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    page = form.submit()
    assert page.has_text("Enter your first name")
    assert page.has_one("p#question-first_name-error.govuk-error-message:contains('Enter your first name')")

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = "07777777777"
    form["email"] = "not-an-email"
    page = form.submit()

    assert page.has_one("p:contains('Invalid email format')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_referral_not_providing_email():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    page = form.submit()
    assert page.has_text("Enter your first name")
    assert page.has_one("p#question-first_name-error.govuk-error-message:contains('Enter your first name')")

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = "07777777777"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Confirm and submit')")

    form = page.get_form()
    page = form.submit()

    assert page.has_text("Please confirm that you agree to the use of your information by checking this box")
    form = page.get_form()
    form["permission"] = True
    form["acknowledge"] = True

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_referral_not_providing_contact_number():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    page = form.submit()
    assert page.has_text("Enter your first name")
    assert page.has_one("p#question-first_name-error.govuk-error-message:contains('Enter your first name')")

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["email"] = "freddy.flibble@example.com"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Confirm and submit')")

    form = page.get_form()
    page = form.submit()

    assert page.has_text("Please confirm that you agree to the use of your information by checking this box")
    form = page.get_form()
    form["permission"] = True
    form["acknowledge"] = True

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()


@pytest.mark.parametrize(
    ("postcode", "valid"),
    [
        ("This isn't a postcode", False),
        ("This is not a postcode", False),
        ("AA11AAA", False),
        ("1", False),
        ("A", False),
        ("A1", False),
        ("L15", False),
        ("L2A", False),
        ("1111111", False),
        ("EC1A 1BB", True),
        ("W1A 0AX", True),
        ("M1 1AE", True),
        ("B33 8TH", True),
        ("CR2 6XH", True),
        ("DN55 1PT", True),
    ],
)
@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_postcode_validation(postcode, valid):
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = 1
    form["postcode"] = postcode

    if valid:
        page = form.submit().follow()
        assert page.has_one('h1:contains("Select your address")')
    else:
        page = form.submit()
        assert page.has_text("Enter a valid UK postcode")


def test_address_length_validation():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "?" * 256
    form["postcode"] = "?" * 256
    page = form.submit()

    assert page.has_text("Longer than maximum length 128")
    assert page.has_text("Enter a valid UK postcode")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_bulb_to_octopus():
    supplier = "Bulb, now part of Octopus Energy"

    session_id, _ = _do_happy_flow(supplier=supplier)

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")
    assert "Your details have been submitted to Octopus Energy." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == "Octopus Energy"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_utility_warehouse_to_eon():
    supplier = "Utility Warehouse"

    session_id, _ = _do_happy_flow(supplier=supplier)

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")
    assert "Your details have been submitted to E.ON Next." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == "E.ON Next"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_should_send_referral_to_octopus_when_shell_is_selected():
    supplier = "Shell"

    session_id, _ = _do_happy_flow(supplier=supplier)

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")
    assert "Your details have been submitted to Octopus Energy." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == "Octopus Energy"
    referral.delete()


def test_shell_redirects_to_warning():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Shell")

    assert page.has_one("h1:contains('Your referral will be sent to Octopus Energy')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
@pytest.mark.parametrize("has_loft_insulation", [True, False])
def test_on_check_page_back_button_goes_to_correct_location(has_loft_insulation):
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
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
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", "Yes")

    assert page.has_one("h1:contains('What kind of property do you have?')")
    page = _check_page(page, "property-type", "property_type", "House")

    assert page.has_one("h1:contains('What kind of house do you have?')")
    page = _check_page(page, "property-subtype", "property_subtype", "Detached")

    assert page.has_one("h1:contains('How many bedrooms does the property have?')")
    page = _check_page(page, "number-of-bedrooms", "number_of_bedrooms", "Two bedrooms")

    assert page.has_one("h1:contains('What kind of walls does your property have?')")
    page = _check_page(page, "wall-type", "wall_type", "Cavity walls")

    assert page.has_one("h1:contains('Are your walls insulated?')")
    page = _check_page(page, "wall-insulation", "wall_insulation", "No they are not insulated")

    assert page.has_one("h1:contains('Do you have a loft that has not been converted into a room?')")
    if has_loft_insulation:
        page = _check_page(page, "loft", "loft", "Yes, I have a loft that has not been converted into a room")

        assert page.has_one("h1:contains('Is there access to your loft?')")
        page = _check_page(page, "loft-access", "loft_access", "Yes, there is access to my loft")

        assert page.has_one("h1:contains('How much loft insulation do you have?')")
        page = _check_page(
            page, "loft-insulation", "loft_insulation", "I have less than or equal to 100mm of loft insulation"
        )
    else:
        page = _check_page(page, "loft", "loft", "No, I do not have a loft or my loft has been converted into a room")

    assert page.has_one("h1:contains('Check your answers')")

    page = page.click(contains="Back")

    if has_loft_insulation:
        assert page.has_one("h1:contains('How much loft insulation do you have?')")
    else:
        assert page.has_one("h1:contains('Do you have a loft that has not been converted into a room?')")


def test_switching_path_to_social_housing_does_not_ask_park_home_questions_again():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    assert page.has_text("Where is the property located?")
    page = _check_page(page, "country", "country", "England")

    assert page.has_text("Select your home energy supplier from the list below")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "Yes")

    assert page.has_text("Is the park home your main residence?")
    page = page.click(contains="Back")

    assert page.has_text("Is the property a park home?")
    page = page.click(contains="Back")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "No, I am a social housing tenant")

    assert page.has_text("What is the property's address?")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_check_answers_page_changing_to_social_housing_hides_park_home_question():
    _check_page, page, session_id = _setup_client_and_page()

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes")

    # press back to get to summary page
    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Check your answers')")

    _assert_change_button_is_not_hidden(page, "park-home")

    page = _click_change_button(page, "own-property")
    assert page.has_text("Do you own the property?")

    page = _check_page(page, "own-property", "own_property", "No, I am a social housing tenant")
    assert page.has_one("h1:contains('Check your answers')")

    _assert_change_button_is_hidden(page, "park-home")
    _assert_change_button_is_hidden(page, "park-home-main-residence")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
@pytest.mark.parametrize("park_home", [True, False])
def test_on_check_answers_page_if_park_home_main_residence_is_hidden_depending_on_park_home_answer(park_home):
    _check_page, page, session_id = _setup_client_and_page()

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", park_home=park_home)

    # press back to get to summary page
    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Check your answers')")

    if park_home:
        _assert_change_button_is_not_hidden(page, "park-home-main-residence")
    else:
        _assert_change_button_is_hidden(page, "park-home-main-residence")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_check_answers_page_changing_to_no_loft_hides_loft_follow_up_questions():
    _check_page, page, session_id = _setup_client_and_page()

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", has_loft=True)

    # press back to get to summary page
    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Check your answers')")

    _assert_change_button_is_not_hidden(page, "loft-access")
    _assert_change_button_is_not_hidden(page, "loft-insulation")

    page = _click_change_button(page, "loft")
    assert page.has_text("Do you have a loft that has not been converted into a room?")

    page = _check_page(page, "loft", "loft", "No, I do not have a loft or my loft has been converted into a room")
    assert page.has_one("h1:contains('Check your answers')")

    _assert_change_button_is_hidden(page, "loft-access")
    _assert_change_button_is_hidden(page, "loft-insulation")


# lots of cases sourced from
# https://gist.github.com/edwardhorsford/a9df6b16a561cd54336fbba51572db25
@pytest.mark.parametrize(
    ("contact_number", "expect_to_accept"),
    [
        ("1234", True),
        ("01632 960 001", True),
        ("07700 900 982", True),
        ("+44 808 157 0192", True),
        ("+33 06 12 34 56 78", True),
        ("07700900456", True),
        ("+447700900456", True),
        ("(+44) 07700900456", True),
        ("07700 900 456", True),
        ("07700 900456", True),
        ("+447700 900456", True),
        ("01144960573", True),
        ("+441144960573", True),
        ("+44114 4960573", True),
        ("0114 4960573", True),
        ("0114 496 0573", True),
        ("(0114) 496 0573", True),
        ("(0114) 4960573", True),
        ("02079460000", True),
        ("+442079460000", True),
        ("020 79460000", True),
        ("020 7946 0000", True),
        ("01632960123", True),
        ("+441632960123", True),
        ("+441632 960123", True),
        ("01632 960123", True),
        ("01632 960 123", True),
        ("(01632) 960123", True),
        ("(01632) 960 123", True),
        ("0169772551", True),
        ("0169 772551", True),
        ("0169 772 551", True),
        ("(0169) 772551", True),
        ("(0169) 772 551", True),
        ("1", False),
        ("12", False),
        ("123", False),
        ("not a number", False),
    ],
)
@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_contact_details_page_correct_phone_numbers_are_accepted(contact_number, expect_to_accept):
    _check_page, page, session_id = _setup_client_and_page()

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", has_loft=True)

    assert page.has_one("h1:contains('We think you might be eligible')")
    assert page.has_text("Great British Insulation Scheme")
    form = page.get_form()
    form["ventilation_acknowledgement"] = True
    page = form.submit().follow()

    assert page.has_one("h1:contains('Add your personal and contact details')")
    form = page.get_form()

    form["first_name"] = "Freddy"
    form["last_name"] = "Flibble"
    form["contact_number"] = contact_number
    form["email"] = "freddy.flibble@example.com"

    if expect_to_accept:
        page = form.submit().follow()
        assert page.has_one("h1:contains('Confirm and submit')")
    else:
        page = form.submit()
        assert page.has_text("Enter a telephone number, like 01632 960 001, 07700 900 982 or +44 808 157 0192")
        assert page.has_one(
            "p#question-contact_number-error.govuk-error-message:contains('Enter a telephone number, like "
            "01632 960 001, 07700 900 982 or +44 808 157 0192')"
        )


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_success_page_on_yes_to_benefits_eco4_is_shown():
    supplier = "British Gas"

    _, page = _do_happy_flow(supplier=supplier, benefits_answer="Yes")

    assert page.has_text(
        f"{supplier} or their installation partner may also check if your home is suitable for more "
        "help with energy efficiency improvements through the ECO4 scheme"
    )


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_success_page_on_no_to_benefits_income_less_than_31k_eco4_is_shown():
    supplier = "British Gas"

    _, page = _do_happy_flow(supplier=supplier, benefits_answer="No")

    assert page.has_text(
        f"{supplier} or their installation partner may also check if your home is suitable for more "
        "help with energy efficiency improvements through the ECO4 scheme"
    )


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_success_page_on_no_to_benefits_income_more_than_31k_eco4_is_not_shown():
    supplier = "British Gas"

    # to fulfill neither requirement but still be eligible, be in a park home
    _, page = _do_happy_flow(
        supplier=supplier, park_home=True, benefits_answer="No", household_income="£31,000 or more a year"
    )

    assert not page.has_text(
        f"{supplier} or their installation partner may also check if your home is suitable for "
        "more help with energy efficiency improvements through the ECO4 scheme"
    )


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_submitting_a_recent_uprn_twice_the_referral_already_submitted_page_is_shown():
    supplier = "British Gas"
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    utils.create_referral(session_id=session_id, supplier=supplier)

    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = supplier
    page = form.submit().follow()

    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form["lmk"] = "222222222222222222222222222222222"
    page = form.submit().follow()

    assert page.has_one("h1:contains('A referral has already been submitted')")
    assert page.has_text("The information you have submitted matches a referral made on")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_submitting_a_uprn_which_does_not_have_recent_duplicate_already_submitted_page_is_not_shown():
    supplier = "British Gas"
    not_recent_date = timezone.now() + relativedelta(months=-12)

    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    utils.create_referral(session_id=session_id, supplier=supplier, creation_timestamp=not_recent_date)

    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Octopus Energy"
    page = form.submit().follow()

    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "10"
    form["postcode"] = "SW1A 2AA"
    page = form.submit().follow()

    form = page.get_form()
    form["lmk"] = "222222222222222222222222222222222"
    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the council tax band of your property?')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_submitting_a_recent_uprn_twice_to_different_suppliers_the_referral_already_submitted_page_is_shown():
    supplier = "British Gas"
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    utils.create_referral(session_id=session_id, supplier=supplier)

    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Octopus Energy"
    page = form.submit().follow()

    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "10"
    form["postcode"] = "SW1A 2AA"
    page = form.submit().follow()

    form = page.get_form()
    form["lmk"] = "222222222222222222222222222222222"
    page = form.submit().follow()

    assert page.has_one("h1:contains('A referral has already been submitted')")
    assert page.has_text("The information you have submitted matches a referral made to another energy supplier")


def test_on_skipping_to_supplier_page_on_country_page_the_sorry_journey_page_is_shown():
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    page = client.get(f"{session_id}/supplier")
    page = page.follow().follow()

    assert page.has_one("h1:contains('Page not found')")
    assert page.has_text("You're not able to see this page.")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_on_epc_select_page_enter_manually_can_be_selected():
    client = utils.get_client()
    page = client.get("/start")
    page = page.follow()

    session_id = page.path.split("/")[1]

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Octopus Energy"
    page = form.submit().follow()

    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "10"
    form["postcode"] = "SW1A 2AA"
    page = form.submit().follow()

    assert page.has_one("label:contains('I cannot find my address, I want to enter it manually')")

    form = page.get_form()
    form["lmk"] = "enter-manually"
    page = form.submit().follow()

    assert page.has_one('h1:contains("What is the property\'s address?")')


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_epc_page_shows_epc_info():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
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
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    assert page.has_one("p:contains('Registered address')")
    assert page.has_one("p:contains('22 Acacia Avenue')")
    assert page.has_one("p:contains('Upper Wellgood')")
    assert page.has_one("p:contains('Fulchester')")
    assert page.has_one("p:contains('FL23 4JA')")

    assert page.has_one("p:contains('Property type')")
    assert page.has_one("p:contains('Maisonette')")

    assert page.has_one("p:contains('EPC rating')")
    assert page.has_one("p:contains('G')")

    assert page.has_one("p:contains('Date of issue')")
    assert page.has_one("p:contains('23 July 2010')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApiWithMultipleEPC)
def test_epc_select_only_shows_most_recent_epc_per_uprn():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name=address_page)

    assert page.has_one("label:contains('22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA')")

    assert len(data[address_all_address_and_details_field]) == 1
    assert data[address_all_address_and_details_field][0]["lmk-key"] != "3333333333333333333333333333333333"


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockRecommendationsNotFoundEPCApi)
def test_on_recommendations_not_found_response_recommendations_are_empty_list():
    _get_empty_recommendations_journey()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockRecommendationsInternalServerErrorEPCApi)
def test_on_recommendations_internal_server_error_response_recommendations_are_empty_list():
    _get_empty_recommendations_journey()


def _get_empty_recommendations_journey():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form[country_field] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form[supplier_field] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form[address_building_name_or_number_field] = "22"
    form[address_postcode_field] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form[lmk_field] = "222222222222222222222222222222222"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc-select")
    assert data[recommendations_field] == []

    assert page.has_one("h1:contains('What is the council tax band of your property?')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockRecommendationsTransientInternalServerErrorEPCApi)
def test_on_recommendations_transient_internal_server_error_response_recommendations_are_empty_list():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form[country_field] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form[supplier_field] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form[address_building_name_or_number_field] = "22"
    form[address_postcode_field] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form[lmk_field] = "222222222222222222222222222222222"
    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_success_page_still_shows_if_journey_cannot_reach_it():
    supplier = "Utilita"

    session_id, _ = _do_happy_flow(supplier=supplier)

    utils.delete_answer_in_session(session_id, country_page)

    client = utils.get_client()
    page = client.get(f"/{session_id}/success").follow()

    assert page.has_one(f"h1:contains('Your details have been submitted to {supplier}')")


@unittest.mock.patch(
    "help_to_heat.frontdoor.interface.EPCApi", get_mock_epc_api_expecting_address_and_postcode("22", "FL23 4JA")
)
def test_epc_api_is_called_with_trimmed_address_and_postcode():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    form = page.get_form()
    form["supplier"] = "Utilita"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Is the property a park home?")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "  22  "
    form["postcode"] = "  FL23 4JA  "
    page = form.submit().follow()

    assert page.has_one("label:contains('22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA')")
    assert page.has_one("label:contains('11 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA')")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_alternative_supplier_is_shown_in_referrals():
    supplier = supplier_field_utilita
    session_id, _ = _do_happy_flow(supplier=supplier, use_alternative=True)

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == supplier
    assert referral.data.get(supplier_field) == supplier
    assert referral.data.get(user_selected_supplier_field) == supplier
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_alternative_supplier_is_shown_in_referrals_when_handled_by_a_different_supplier():
    session_id, _ = _do_happy_flow(supplier=supplier_field_utility_warehouse, use_alternative=True)

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == supplier_field_eon_next
    assert referral.data.get(supplier_field) == supplier_field_eon_next
    assert referral.data.get(user_selected_supplier_field) == supplier_field_utility_warehouse
    referral.delete()


def _setup_client_and_page():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()
    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)
    _check_page = _make_check_page(session_id)
    return _check_page, page, session_id
