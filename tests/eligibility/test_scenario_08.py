import itertools

import pytest

from help_to_heat.frontdoor.eligibility import country_council_tax_bands
from tests.test_eligibility import countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU, \
    household_incomes, own_property_owner, yes, _run_scenario, accept_both


def test_scenario_8():
    own_property = own_property_owner
    benefits = yes

    for (country, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both
