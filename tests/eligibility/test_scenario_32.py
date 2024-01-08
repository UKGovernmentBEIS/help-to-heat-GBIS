import pytest

from tests.test_eligibility import countries_england_scotland_wales, council_tax_bands, epc_DEFGU, yes_no, \
    household_incomes, _run_scenario, own_property_social_housing, yes, accept_both, property_types


@pytest.mark.parametrize("country", countries_england_scotland_wales)
@pytest.mark.parametrize("property_type", property_types)
@pytest.mark.parametrize("council_tax_band", council_tax_bands)
@pytest.mark.parametrize("epc_rating", epc_DEFGU)
@pytest.mark.parametrize("benefits", yes_no)
@pytest.mark.parametrize("household_income", household_incomes)
def test_scenario_32(country, property_type, council_tax_band, epc_rating, benefits, household_income):
    assert _run_scenario(country, own_property_social_housing, property_type, yes, council_tax_band, epc_rating,
                         benefits, household_income) == accept_both
