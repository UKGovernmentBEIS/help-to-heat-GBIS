import csv
import unittest

import freezegun

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.mock_os_api import MockOSApi

from . import utils
from .test_frontdoor import _do_happy_flow


@unittest.mock.patch("help_to_heat.frontdoor.os_api.OSApi", MockOSApi)
@utils.mock_os_api
def test_csv():
    expected_datetime = "2022-06-30 23:59:59+00:00"
    with freezegun.freeze_time(expected_datetime):
        _do_happy_flow(supplier="EON")

    client = utils.get_client()
    page = utils.login_as_team_leader(client, supplier="EON")
    assert page.has_one("p:contains('Unread leads') ~ p:contains('1')")

    download_datetime = "2022-07-31 23:48:59+00:00"
    with freezegun.freeze_time(download_datetime):
        csv_page = page.click(contains="Download latest leads")

    page = client.get("/portal/")
    assert page.has_one("span:contains('2022-08-01')")
    assert page.has_one("span:contains('00:48')")

    text = csv_page.content.decode("utf-8")
    lines = text.splitlines()
    assert len(lines) == 2
    assert len(lines[0].split(",")) == 29, len(lines[0].split(","))

    rows = list(csv.DictReader(lines))
    data = rows[0]
    assert data["epc_date"] == "2022-12-25"
    assert data["submission_date"] == "2022-07-01"
    assert data["submission_time"] == "00:59:59"


@unittest.mock.patch("help_to_heat.frontdoor.os_api.OSApi", MockOSApi)
@utils.mock_os_api
def test_referral_created_at():
    expected_datetime = "2022-12-25 14:34:56+00:00"
    with freezegun.freeze_time(expected_datetime):
        session_id = _do_happy_flow(supplier="EON")

    data = interface.api.session.get_session(session_id)

    assert data["referral_created_at"] == expected_datetime, (expected_datetime, data["referral_created_at"])
