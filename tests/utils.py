import functools
import os
import pathlib
import random
import re
import string

import furl
import httpx
import pyotp
import requests_mock
import testino
from django.conf import settings
from django.utils import timezone

from help_to_heat import portal, wsgi
from help_to_heat.portal import models

__here__ = pathlib.Path(__file__).parent

DATA_DIR = __here__ / "data"

TEST_SERVER_URL = "http://help-to-heat-testserver/"


def mock_os_api(func):
    uprn_data = (DATA_DIR / "sample_os_api_uprn_response.json").read_text()

    @functools.wraps(func)
    def _inner(*args, **kwargs):
        with requests_mock.Mocker() as m:
            m.register_uri(requests_mock.ANY, re.compile(TEST_SERVER_URL + ".*"), real_http=True)
            m.register_uri("GET", "https://api.os.uk/search/places/v1/uprn", text=uprn_data)
            return func(*args, **kwargs)

    return _inner


def make_code(length=6):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def with_client(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        with httpx.Client(app=wsgi.application, base_url=TEST_SERVER_URL) as client:
            return func(client, *args, **kwargs)

    return _inner


def get_client():
    return testino.WSGIAgent(wsgi.application, base_url=TEST_SERVER_URL)


def wipe_emails():
    email_dir = pathlib.Path(settings.EMAIL_FILE_PATH)
    if email_dir.exists():
        for f in email_dir.iterdir():
            if f.is_file():
                f.unlink()


def get_latest_email_text(email):
    email_dir = pathlib.Path(settings.EMAIL_FILE_PATH)
    latest_email_path = max(email_dir.iterdir(), key=os.path.getmtime)
    content = latest_email_path.read_text()
    assert f"To: {email}" in content.splitlines(), (f"To: {email}", content.splitlines())
    return content


def get_latest_email_url(email):
    text = get_latest_email_text(email)
    lines = text.splitlines()
    url_lines = tuple(word for line in lines for word in line.split() if word.startswith(settings.BASE_URL))
    assert len(url_lines) == 1
    email_url = url_lines[0].strip()
    email_url = furl.furl(email_url)
    email_url = email_url.tostr()
    return email_url


def login_as_service_manager(client, email=None, password=None, supplier="Utilita"):
    return login_as_role(client, "SERVICE_MANAGER", email=email, password=password, supplier=supplier)


def login_as_team_leader(client, email=None, password=None, supplier="Utilita"):
    return login_as_role(client, "TEAM_LEADER", email=email, password=password, supplier=supplier)


def login_as_role(client, role, email=None, password=None, supplier="Utilita"):
    assert role in ("TEAM_LEADER", "SERVICE_MANAGER")
    if not email:
        email = f"{role.replace('_', '-')}+{make_code()}@example.com"
    if not password:
        password = "Fl1bbl3Fl1bbl3"
    user = models.User.objects.create_user(email, password)
    user.full_name = f"Test {role.replace('_', ' ').capitalize()}"
    user.invite_accepted_at = timezone.now()
    user.role = role
    if role == "TEAM_LEADER":
        user.supplier_id = models.Supplier.objects.get(name=supplier).id
    user.save()
    page = login(client, email, password)
    assert page.has_text("Logout")
    return page


def login(client, email, password):
    page = client.get("/portal/accounts/login/")
    form = page.get_form()
    form["login"] = email
    form["password"] = password
    page = form.submit()
    page = page.follow()

    assert page.has_text("Please enter your One Time Password (OTP)")

    user = models.User.objects.get(email=email.lower())
    secret = user.get_totp_secret()

    form = page.get_form()
    form["otp"] = get_otp(secret)
    page = form.submit().follow()

    return page


def get_otp(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()


def create_referral(session_id, data=None, supplier="British Gas", creation_timestamp=timezone.now()):
    if data is None:
        data = {
            "lmk": "222222222222222222222222222222222",
            "loft": "No, I do not have a loft or my loft has been converted into a room",
            "uprn": "001234567890",
            "email": "example@example.com",
            "county": "London",
            "address": "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA",
            "country": "England",
            "schemes": ["GBIS", "ECO4"],
            "benefits": "No",
            "epc_date": "",
            "postcode": "SW1A 2AA",
            "supplier": supplier,
            "last_name": "Flimble",
            "park_home": "No",
            "wall_type": "I do not know",
            "epc_rating": "Not found",
            "first_name": "Flooble",
            "epc_details": {},
            "loft_access": "No loft",
            "own_property": "Yes, I own my property and live in it",
            "town_or_city": "London",
            "property_type": "House",
            "address_line_1": "10, DOWNING STREET",
            "address_line_2": "LONDON",
            "contact_number": "",
            "loft_insulation": "No loft",
            "wall_insulation": "I do not know",
            "council_tax_band": "A",
            "household_income": "Less than £31,000 a year",
            "property_subtype": "Semi-detached",
            "number_of_bedrooms": "Two bedrooms",
            "accept_suggested_epc": "Not found",
            "user_selected_supplier": "British Gas",
            "building_name_or_number": "10",
        }
    supplier = portal.models.Supplier.objects.get(name=data["supplier"])
    referral = portal.models.Referral.objects.create(session_id=session_id, data=data, supplier=supplier)
    referral.save()
    referral = portal.models.Referral.objects.get()
    referral.created_at = creation_timestamp
    referral.save()
