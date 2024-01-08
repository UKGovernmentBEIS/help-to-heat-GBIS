import pytest

from tests.test_eligibility import countries_not_england_scotland_wales, property_types, council_tax_bands, epcs, \
    _run_scenario, own_property_options, yes_no,yes,  household_incomes, deny


@pytest.mark.parametrize("country", countries_not_england_scotland_wales)
@pytest.mark.parametrize("own_property", own_property_options)
@pytest.mark.parametrize("property_type", property_types)
@pytest.mark.parametrize("council_tax_band", council_tax_bands)
@pytest.mark.parametrize("benefits", yes_no)
@pytest.mark.parametrize("household_income", household_incomes)
@pytest.mark.parametrize("epc_rating", epcs)
# a country not in england or wales should fail no matter what else is input
# however testing all other possibilities is too much, so varying only a subset
def test_scenario_1(country, own_property, property_type, council_tax_band, benefits, household_income, epc_rating):
    assert _run_scenario(country, own_property, property_type, yes, council_tax_band, epc_rating,
                         benefits, household_income) == deny
