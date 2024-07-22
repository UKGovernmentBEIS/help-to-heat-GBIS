import pytest

import help_to_heat


@pytest.fixture(autouse=True)
def reset_referrals():
    yield

    help_to_heat.portal.models.Referral.objects.all().delete()
