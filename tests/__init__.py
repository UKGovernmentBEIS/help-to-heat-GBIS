import os

import django
import pytest

import help_to_heat

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "help_to_heat.settings")
django.setup()

@pytest.fixture(autouse=True)
def reset_referrals():
    help_to_heat.portal.models.Referral.objects.all().delete()

    yield
