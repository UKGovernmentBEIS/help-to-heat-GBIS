import itertools

from tests.test_eligibility import countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, \
    epc_DEFGU, property_type_park_home, yes, no, household_income_less_than_31k, _run_scenario, accept_both


def test_scenario_19():
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = no
    household_income = household_income_less_than_31k

    for (country, own_property, council_tax_band, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epc_DEFGU):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both
