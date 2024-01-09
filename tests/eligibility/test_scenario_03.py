import itertools

import pytest

from tests.test_eligibility import countries_england_scotland_wales, council_tax_bands, epc_ABC, yes_no, \
    household_incomes, own_property_owner, property_type_park_home, yes, _run_scenario, deny


def test_scenario_3():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes

    for (country, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, council_tax_bands, epc_ABC, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny
