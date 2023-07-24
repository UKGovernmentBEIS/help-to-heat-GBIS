import datetime
import random
import string
import pytest

import django.db.utils

from . import utils

from help_to_heat.portal import models

from . import utils


def test_epc_duplicates():
    uprn = "".join(random.choices(string.digits, k=5))
    data = {
        "uprn": uprn,
        "rating": "A",
        "date": datetime.date(2020, 12, 25),
    }
    epc1 = models.EpcRating(**data)
    epc1.save()
    with pytest.raises(django.db.utils.IntegrityError):
        epc2 = models.EpcRating(**data)
        epc2.save()

def test_healthcheck():
    client = utils.get_client()
    result = client.get("/api/healthcheck/")
    assert result.json()["healthy"] is True
    assert result.json()["datetime"]
