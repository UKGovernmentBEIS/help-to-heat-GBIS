import pytest

from tests.test_eligibility import countries_not_england_scotland_wales, property_types, council_tax_bands, epcs, \
    _run_scenario, own_property_owner, yes, household_income_less_than_31k, deny


@pytest.mark.parametrize("country", countries_not_england_scotland_wales)
@pytest.mark.parametrize("property_type", property_types)
@pytest.mark.parametrize("council_tax_band", council_tax_bands)
@pytest.mark.parametrize("epc_rating", epcs)
# a country not in england or wales should fail no matter what else is input
# however testing all other possibilities is too much, so varying only a subset
def test_scenario_1(country, property_type, council_tax_band, epc_rating):
    assert _run_scenario(country, own_property_owner, property_type, yes, council_tax_band, epc_rating,
                         yes, household_income_less_than_31k) == deny
