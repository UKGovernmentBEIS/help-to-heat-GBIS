import itertools

from tests.test_eligibility import countries_not_england_scotland_wales, property_types, council_tax_bands, epcs, \
    _run_scenario, own_property_options, yes_no,yes,  household_incomes, deny


def test_scenario_1():
    for (country, own_property, property_type, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_not_england_scotland_wales, own_property_options, property_types, council_tax_bands, epcs, yes_no, household_incomes):
        # a country not in england or wales should fail no matter what else is input
        # however testing all other possibilities is too much, so varying only a subset
        assert _run_scenario(country, own_property, property_type, yes, council_tax_band, epc_rating,
                             benefits, household_income) == deny
