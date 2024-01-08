import pytest

from tests.test_eligibility import countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, \
    epcs, yes_no, household_incomes, property_type_park_home, no, _run_scenario, deny


@pytest.mark.parametrize("country", countries_england_scotland_wales)
@pytest.mark.parametrize("own_property", own_property_tenant_landlord)
@pytest.mark.parametrize("council_tax_band", council_tax_bands)
@pytest.mark.parametrize("epc_rating", epcs)
@pytest.mark.parametrize("benefits", yes_no)
@pytest.mark.parametrize("household_income", household_incomes)
def test_scenario_15(country, own_property, council_tax_band, epc_rating, benefits, household_income):
    property_type = property_type_park_home
    park_home_main_residence = no

    assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                         benefits, household_income) == deny
