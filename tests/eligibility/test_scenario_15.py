import itertools

from tests.test_eligibility import countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, \
    epcs, yes_no, household_incomes, property_type_park_home, no, _run_scenario, deny


def test_scenario_15():
    property_type = property_type_park_home
    park_home_main_residence = no

    for (country, own_property, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epcs, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny
