import pytest

from help_to_heat.frontdoor.eligibility import country_council_tax_bands
from tests.test_eligibility import countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU, \
    household_incomes, own_property_owner, yes, _run_scenario, accept_both


@pytest.mark.parametrize("country", countries_england_scotland_wales)
@pytest.mark.parametrize("property_type", property_types_not_park_home)
@pytest.mark.parametrize("park_home_main_residence", yes_no)
@pytest.mark.parametrize("epc_rating", epc_DEFGU)
@pytest.mark.parametrize("household_income", household_incomes)
def test_scenario_14(country, property_type, park_home_main_residence, epc_rating, household_income):
    own_property = own_property_owner
    benefits = yes

    for council_tax_band in country_council_tax_bands[country]["ineligible"]:
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both
