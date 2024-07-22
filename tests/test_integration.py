import csv
import unittest
from datetime import datetime, timedelta

import freezegun

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.mock_epc_api import MockEPCApi

from . import utils
from .test_frontdoor import _do_happy_flow


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_csv():
    before_submission = "2022-06-30 23:59:59+00:00"
    with freezegun.freeze_time(before_submission, tick=True):
        _do_happy_flow(supplier="Utilita")
        after_submission = datetime.now()

    client = utils.get_client()
    page = utils.login_as_team_leader(client, supplier="Utilita")
    assert page.has_one("p:contains('Unread leads') ~ p:contains('1')")

    download_datetime = "2022-07-31 23:48:59+00:00"
    with freezegun.freeze_time(download_datetime, tick=True):
        csv_page = page.click(contains="Download latest leads", index=0)

    page = client.get("/portal/")
    assert page.has_one("span:contains('2022-08-01')")
    assert page.has_one("span:contains('00:48')")

    text = csv_page.content.decode("utf-8")
    lines = text.splitlines()
    assert len(lines) == 2
    assert len(lines[0].split(",")) == 33, len(lines[0].split(","))

    rows = list(csv.DictReader(lines))
    data = rows[0]
    assert data["epc_date"] == "2020-02-29"
    assert data["submission_date"] == "2022-07-01"

    before_submission_bst = datetime(2022, 6, 30, 23, 59, 59) + timedelta(hours=1)
    after_submission_bst = after_submission.replace(microsecond=0) + timedelta(hours=1)

    assert f'{data["submission_date"]} {data["submission_time"]}' >= str(before_submission_bst)
    assert f'{data["submission_date"]} {data["submission_time"]}' <= str(after_submission_bst)


@unittest.mock.patch("help_to_heat.frontdoor.interface.EPCApi", MockEPCApi)
def test_referral_created_at():
    before_referral_created = datetime.now()
    session_id, _ = _do_happy_flow(supplier="Utilita")
    after_referral_created = datetime.now()

    data = interface.api.session.get_session(session_id)

    assert data["referral_created_at"] >= str(before_referral_created)
    assert data["referral_created_at"] <= str(after_referral_created)
