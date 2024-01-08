import pytest

from tests.test_eligibility import countries_england_scotland_wales, council_tax_bands, epc_DEFGU, household_incomes, \
    own_property_owner, property_type_park_home, yes, _run_scenario, accept_both


@pytest.mark.parametrize("country", countries_england_scotland_wales)
@pytest.mark.parametrize("council_tax_band", council_tax_bands)
@pytest.mark.parametrize("epc_rating", epc_DEFGU)
@pytest.mark.parametrize("household_income", household_incomes)
def test_scenario_4(country, council_tax_band, epc_rating, household_income):
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = yes

    assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                         benefits, household_income) == accept_both
