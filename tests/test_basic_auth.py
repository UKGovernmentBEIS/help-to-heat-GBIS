import base64
import unittest

from django.conf import settings

from . import utils


@unittest.skipIf(not settings.BASIC_AUTH, "No basic auth set")
def test_homepage_basic_auth():
    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 401

    page = client.get(
        "/start",
        headers={
            "AUTHORIZATION": " ".join(("basic", base64.b64encode(b"mr-flibble:flim-flam-flooble").decode("utf-8")))
        },
    )

    assert page.status_code == 302


@unittest.skipIf(not settings.BASIC_AUTH, "No basic auth set")
def test_portal_basic_auth():
    client = utils.get_client()
    page = client.get("/portal/")
    assert page.status_code == 401
