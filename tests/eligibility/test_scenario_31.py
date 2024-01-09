import itertools

from tests.test_eligibility import countries_england_scotland_wales, council_tax_bands, epc_ABC, yes_no, \
    household_incomes, _run_scenario, own_property_social_housing, yes, deny, property_types


def test_scenario_31():
    for (country, property_type, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, property_types, council_tax_bands, epc_ABC, yes_no, household_incomes):
        assert _run_scenario(country, own_property_social_housing, property_type, yes, council_tax_band, epc_rating,
                             benefits, household_income) == deny
