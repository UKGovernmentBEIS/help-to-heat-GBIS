import datetime
import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor import models as frontdoor_models
from help_to_heat.portal import models

from . import utils


def _add_epc(uprn, rating):
    models.EpcRating.objects.update_or_create(
        uprn=uprn, defaults={"rating": rating, "date": datetime.date(2022, 12, 25)}
    )
    assert interface.api.epc.get_epc(uprn)


def test_flow_northern_ireland():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
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


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_flow_scotland():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Do you own the property?')")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_one("h1:contains('What is the property’s address?')")

    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["address_line_1"] == "999 Letsby Avenue"
    assert data["postcode"] == "PO99 9PO"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")
    page = _check_page(page, "benefits", "benefits", "Yes")


def test_flow_errors():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    page = form.submit()

    assert page.has_one("h2:contains('There is a problem')")
    assert page.has_text("Select where the property is located")


def _answer_house_questions(page, session_id, benefits_answer, epc_rating="D"):
    """Answer main flow with set answers"""
    _add_epc(uprn="100023336956", rating=epc_rating)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_one("h1:contains('What is the property’s address?')")

    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["address_line_1"] == "999 Letsby Avenue"
    assert data["postcode"] == "PO99 9PO"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")
    page = _check_page(page, "benefits", "benefits", benefits_answer)

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

    assert page.has_one("""h1:contains("Do you have a loft that hasn't been converted into a room?")""")
    page = _check_page(page, "loft", "loft", "Yes, I have a loft that hasn't been converted into a room")

    assert page.has_one("h1:contains('Is there access to your loft?')")
    page = _check_page(page, "loft-access", "loft_access", "Yes, there is access to my loft")

    assert page.has_one("h1:contains('Is your loft fully insulated?')")
    page = _check_page(
        page, "loft-insulation", "loft_insulation", "No, there is less than 270mm of insulation in my loft"
    )

    assert page.has_one("h1:contains('Check your answers')")
    form = page.get_form()
    page = form.submit().follow()

    return page


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_happy_flow():
    supplier = "EON"
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


def _do_happy_flow(supplier="Foxglove"):
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", epc_rating="F")

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "OVO")

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

    page = page.click(contains="Change Energy supplier")

    form = page.get_form()
    form["supplier"] = supplier
    page = form.submit().follow()

    assert page.has_one("h1:contains('Confirm and submit')")
    assert page.has_text(supplier)

    form = page.get_form()
    page = form.submit()

    assert page.has_text("Please confirm that you agree to the use of your information by checking this box")
    form = page.get_form()
    form["permission"] = True

    page = form.submit().follow()

    assert page.has_one(f"h1:contains('Your details have been submitted to {supplier}')")

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
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    assert page.has_one("h1:contains('Where is the property located?')")
    assert page.has_one("a:contains('Back')")

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")

    form = page.get_form()
    form["own_property"] = "Yes, I own my property and live in it"
    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the property’s address?')")

    page = page.click(contains="Back")

    form = page.get_form()
    assert form["own_property"] == "Yes, I own my property and live in it"

    page = page.click(contains="Back")

    form = page.get_form()
    assert form["country"] == "England"


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_no_benefits_flow():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _add_epc(uprn="100023336956", rating="A")

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_one("h1:contains('What is the property’s address?')")

    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["address_line_1"] == "999 Letsby Avenue"
    assert data["postcode"] == "PO99 9PO"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")

    form = page.get_form()
    form["accept_suggested_epc"] = "Yes"
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("""h1:contains("It's likely that your home already has suitable energy saving measures")""")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_summary():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
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

    assert page.has_text("10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.EmptyAPI)
def test_no_address():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    assert page.has_one("h1:contains('Where is the property located?')")
    assert page.has_one("a:contains('Back')")

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")

    form = page.get_form()
    form["own_property"] = "Yes, I own my property and live in it"
    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the property’s address?')")
    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    assert page.has_text("No addresses found")
    page = page.click(contains="I want to enter it manually")
    form = page.get_form()
    assert form["address_line_1"] == "999 Letsby Avenue"
    assert form["postcode"] == "PO99 9PO"

    page = form.submit()
    assert page.has_one("h2:contains('There is a problem')")
    assert page.has_text("Enter your Town or city")

    form = page.get_form()
    assert form["address_line_1"] == "999 Letsby Avenue"
    assert form["postcode"] == "PO99 9PO"

    form["address_line_2"] = "Smalltown"
    form["town_or_city"] = "Metropolis"
    form["county"] = "Big County"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-manual")
    assert data["address_line_1"] == "999 Letsby Avenue"
    assert data["town_or_city"] == "Metropolis"
    assert data["address_line_2"] == "Smalltown"
    assert data["town_or_city"] == "Metropolis"
    assert data["county"] == "Big County"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.EmptyAPI)
def test_no_epc():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_one("h1:contains('What is the property’s address?')")

    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    assert page.has_text("No addresses found")
    page = page.click(contains="I want to enter it manually")
    form = page.get_form()
    assert form["address_line_1"] == "999 Letsby Avenue"
    assert form["postcode"] == "PO99 9PO"

    form["town_or_city"] = "Metropolis"

    page = form.submit().follow()

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", "B")

    assert page.has_one("h1:contains('We did not find a complete Energy Performance Certificate for your property')")
    form = page.get_form()
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="epc")

    assert data["epc_rating"] == "Not found"

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_eligibility():
    client = utils.get_client()
    page = client.get("/")

    epc_rating = "D"
    council_tax_band = "G"

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    _add_epc(uprn="100023336956", rating=epc_rating)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = "England"
    page = form.submit().follow()

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_one("h1:contains('What is the property’s address?')")

    form = page.get_form()
    form["address_line_1"] = "999 Letsby Avenue"
    form["postcode"] = "PO99 9PO"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["address_line_1"] == "999 Letsby Avenue"
    assert data["postcode"] == "PO99 9PO"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", council_tax_band)

    assert page.has_one("h1:contains('We found an Energy Performance Certificate that might be yours')")
    page = _check_page(page, "epc", "accept_suggested_epc", "No")

    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Is anyone in your household receiving any of the following benefits?')")
    page = _check_page(page, "benefits", "benefits", "No")

    assert page.has_one("h1:contains('Your property is not eligible')")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_referral_email():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", epc_rating="F")

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

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

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral_email_text = utils.get_latest_email_text("freddy.flibble@example.com")

    assert "Your details have been submitted to Utilita." in referral_email_text
    assert "You do not need to create another referral at any point." in referral_email_text

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()


def test_feedback_no_session():
    client = utils.get_client()
    page = client.get("/")
    page = page.click(contains="feedback")
    form = page.get_form()
    form["how-much"] = "Agree"
    form["guidance-detail"] = "Completely disagree"
    form["accuracy-detail"] = "Disagree"
    form["more-detail"] = "Blah, blah, blah"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Thank you for your feedback')")
    assert not page.all("a:contains('Back')")

    feedback = frontdoor_models.Feedback.objects.latest("created_at")
    assert feedback.data["how-much"] == "Agree"
    assert feedback.data["guidance-detail"] == "Completely disagree"
    assert feedback.data["accuracy-detail"] == "Disagree"
    assert feedback.data["more-detail"] == "Blah, blah, blah"


def test_feedback_with_session():
    client = utils.get_client()
    page = client.get("/")

    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    form = page.get_form()
    form["country"] = "Scotland"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Do you own the property?')")

    page = page.click(contains="feedback")
    form = page.get_form()
    form["how-much"] = "Agree"
    form["guidance-detail"] = "Completely disagree"
    form["accuracy-detail"] = "Disagree"
    form["more-detail"] = "Blah, blah, blah"
    page = form.submit().follow()

    assert page.has_one("h1:contains('Thank you for your feedback')")

    feedback = frontdoor_models.Feedback.objects.latest("created_at")
    assert feedback.data["how-much"] == "Agree"
    assert feedback.data["guidance-detail"] == "Completely disagree"
    assert feedback.data["accuracy-detail"] == "Disagree"
    assert feedback.data["more-detail"] == "Blah, blah, blah"

    feedback_session_id = page.path.split("/")[3]
    assert uuid.UUID(feedback_session_id)

    page = page.click(contains="Back")
    assert page.has_one("h1:contains('Do you own the property?')")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_incorrect_referral_email():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", epc_rating="F")

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

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

    assert page.has_one("p:contains('Not a valid email address.')")


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_referral_not_providing_email():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", epc_rating="F")

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

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

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()


@unittest.mock.patch("osdatahub.PlacesAPI", utils.StubAPI)
def test_referral_not_providing_contact_number():
    client = utils.get_client()
    page = client.get("/")

    assert page.status_code == 200
    assert page.has_one("h1:contains('Check if you may be eligible for the Great British Insulation Scheme')")

    page = page.click(contains="Start")
    assert page.status_code == 200

    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    # Answer main flow
    page = _answer_house_questions(page, session_id, benefits_answer="Yes", epc_rating="F")

    assert page.has_one("h1:contains('Information based on your answers')")
    assert page.has_text("Great British Insulation Scheme")
    assert not page.has_text("Energy Company Obligation 4")
    form = page.get_form()
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

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

    page = form.submit().follow()

    assert page.has_one("h1:contains('Your details have been submitted to Utilita')")

    referral = models.Referral.objects.get(session_id=session_id)
    referral.delete()
