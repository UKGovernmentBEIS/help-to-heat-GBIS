import functools
import json
import os
import pathlib
import random
import string

import furl
import httpx
import pyotp
import requests_mock
import testino
from django.conf import settings
from django.utils import timezone

from help_to_heat import wsgi
from help_to_heat.portal import models

__here__ = pathlib.Path(__file__).parent
DATA_DIR = __here__ / "data"

TEST_SERVER_URL = "http://help-to-heat-testserver/"


class StubAPI:
    files = {
        "postcode": "sample_osdatahub_postcode_response.json",
        "uprn": "sample_osdatahub_uprn_response.json",
    }

    def __init__(self, key):
        self.key = key

    def postcode(self, text, dataset=None):
        content = (DATA_DIR / self.files["postcode"]).read_text()
        data = json.loads(content)
        return data

    def uprn(self, uprn, dataset=None):
        content = (DATA_DIR / self.files["uprn"]).read_text()
        data = json.loads(content)
        return data


class EmptyAPI(StubAPI):
    files = {
        "postcode": "empty_osdatahub_response.json",
        "uprn": "empty_osdatahub_response.json",
    }


def mock_os_api(func):
    postcode_data = (DATA_DIR / "sample_os_api_postcode_response.json").read_text()
    uprn_data = (DATA_DIR / "sample_os_api_uprn_response.json").read_text()

    @functools.wraps(func)
    def _inner(*args, **kwargs):
        with requests_mock.Mocker() as m:
            m.register_uri("GET", "https://api.os.uk/search/places/v1/postcode", text=postcode_data)
            m.register_uri("GET", "https://api.os.uk/search/places/v1/uprn", text=uprn_data)
            return func()

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
