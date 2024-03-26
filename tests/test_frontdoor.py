import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.mock_epc_api import (
    MockEPCApi,
    MockEPCApiWithEPCC,
    MockNotFoundEPCApi,
    NotFoundRequestException,
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
def _answer_house_questions(page, session_id, benefits_answer, supplier="Utilita"):
    """Answer main flow with set answers"""

    _check_page = _make_check_page(session_id)

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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form["rrn"] = "2222-2222-2222-2222-2222"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc-select")
    assert data["rrn"] == "2222-2222-2222-2222-2222"
    assert data["address"] == "22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", benefits_answer)

    if benefits_answer == "No":
        assert page.has_one("h1:contains('What is your annual household income?')")
        page = _check_page(page, "household-income", "household_income", "Less than £31,000 a year")

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
    page = _check_page(page, "loft-insulation", "loft_insulation", "I have up to 100mm of loft insulation")

    assert page.has_one("h1:contains('Check your answers')")
    form = page.get_form()
    page = form.submit().follow()

    return page


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_happy_flow():
    supplier = "Utilita"
    session_id = _do_happy_flow(supplier=supplier)

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
def _do_happy_flow(supplier="EON"):
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", supplier=supplier)

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
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

    return session_id


def _make_check_page(session_id):
    def _check_page(page, page_name, key, answer):
        form = page.get_form()
        form[key] = answer
        page = form.submit().follow()

        data = interface.api.session.get_answer(session_id, page_name=page_name)
        assert data[key] == answer
        return page

    return _check_page


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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form["rrn"] = "2222-2222-2222-2222-2222"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc-select")
    assert data["rrn"] == "2222-2222-2222-2222-2222"
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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    assert page.has_text("No addresses found")
    page = page.click(contains="I want to enter it manually")
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
    assert data["uprn"] == "100023336956"
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    try:
        assert page.has_one("h1:contains('What is the council tax band of your property?')")
        page = _check_page(page, "council-tax-band", "council_tax_band", "B")
    except NotFoundRequestException:
        page = _check_page(page, "benefits", "benefits", "Yes")

        assert page.has_one("h1:contains('What is your annual household income?')")
        page = _check_page(page, "household-income", "household_income", "Less than £31,000 a year")

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

        assert page.has_one("h1:contains('Is your loft fully insulated?')")
        page = _check_page(
            page, "loft-insulation", "loft_insulation", "No, there is less than 270mm of insulation in my loft"
        )

        assert page.has_one("h1:contains('Check your answers')")
        form = page.get_form()
        page = form.submit().follow()

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


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockNotFoundEPCApi)
@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", EmptyOSApi)
def test_no_epc():
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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    assert page.has_text("No addresses found")
    page = page.click(contains="I want to enter it manually")
    form = page.get_form()
    # TODO: find out if we should still be forwarding this part through, and if so fix it so we are
    assert form["address_line_1"] == ""
    assert form["postcode"] == "FL23 4JA"

    # TODO: won't need to set this if it's passed through from the lookup (see above)
    form["address_line_1"] = "22 Acacia Avenue"
    form["town_or_city"] = "Metropolis"

    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")


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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "22"
    form["postcode"] = "FL23 4JA"
    page = form.submit().follow()

    form = page.get_form()
    form["rrn"] = "2222-2222-2222-2222-2222"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc-select")
    assert data["rrn"] == "2222-2222-2222-2222-2222"
    assert data["address"] == "22 Acacia Avenue, Upper Wellgood, Fulchester, FL23 4JA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", council_tax_band)

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "No")

    page = _check_page(page, "benefits", "benefits", "No")

    page = _check_page(page, "household-income", "household_income", "£31,000 or more a year")

    assert page.has_one("h1:contains('Your property is not eligible')")


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

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
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
    assert "You do not need to create another referral at any point." in referral_email_text

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

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
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

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
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

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
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


def test_address_validation():
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

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "?" * 256
    form["postcode"] = "?" * 256
    page = form.submit()

    assert page.has_text("Longer than maximum length 128")
    assert page.has_text("Please enter a valid UK postcode")


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_bulb_to_octopus():
    supplier = "Bulb, now part of Octopus Energy"

    session_id = _do_happy_flow(supplier=supplier)

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")
    assert "Your details have been submitted to Octopus Energy." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == "Octopus Energy"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_utility_warehouse_to_eon():
    supplier = "Utility Warehouse"

    session_id = _do_happy_flow(supplier=supplier)

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")
    assert "Your details have been submitted to E.ON Next." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    assert referral.supplier.name == "E.ON Next"
    referral.delete()


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_should_send_referral_to_octopus_when_shell_is_selected():
    supplier = "Shell"

    session_id = _do_happy_flow(supplier=supplier)

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
