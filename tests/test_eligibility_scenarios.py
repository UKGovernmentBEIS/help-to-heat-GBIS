import itertools

from help_to_heat.frontdoor.eligibility import (
    calculate_eligibility,
    eligible_for_gbis,
    eligible_for_gbis_and_eco4,
    not_eligible,
)

# Eligibility scenarios were provided in a document on this Jira ticket:
# https://beisdigital.atlassian.net/browse/PC-605
#
# The general format given was (e.g.):
#
# Scenario 18
# - England, Scotland or Wales? Y
# - Property ownership? Tenant or landlord
# - Park home? Y
# - Main residence? Y
# - EPC A, B, C? N
# - Receiving benefits? N
# - Income <£31,000? N
# - [Eligible for GBIS]
#
# These tests are structured to closely match that format for ease of comparison and validation.


# Country

england = "England"
scotland = "Scotland"
wales = "Wales"
northern_ireland = "Northern Ireland"
countries = england, scotland, wales, northern_ireland

# Owner type

owner_occupier = "Yes, I own my property and live in it"
tenant = "No, I am a tenant"
landlord = "Yes, I am the property owner but I lease the property to one or more tenants"
social_housing = "No, I am a social housing tenant"
owner_types = owner_occupier, tenant, landlord, social_housing

# Property type

house = "House"
bungalow = "Bungalow"
apartment_flat_or_maisonette = "Apartment, flat or maisonette"
park_home = "Park home"
property_types = house, bungalow, apartment_flat_or_maisonette, park_home

# Band (Council Tax and EPC)

a = "A"
b = "B"
c = "C"
d = "D"
e = "E"
f = "F"
g = "G"
h = "H"
i = "I"
not_found = "Not found"

council_tax_bands = a, b, c, d, e, f, g, h, i
epc_ratings = a, b, c, d, e, f, g, not_found

# Household income

less_than_31k = "Less than £31,000 a year"
more_than_31k = "£31,000 or more a year"

household_incomes = less_than_31k, more_than_31k

# Yes / no

yes = "Yes"
no = "No"
i_do_not_know = "I do not know"

yes_no = yes, no

def _get_country_options(scenario):
    is_england_scotland_or_wales = scenario.get("England, Scotland or Wales?")
    if is_england_scotland_or_wales is None:
        return countries
    return (england, scotland, wales) if is_england_scotland_or_wales else (northern_ireland,)


def _get_own_property_options(scenario):
    property_ownership = scenario.get("Property ownership?")
    if property_ownership == "Owner occupier":
        return (owner_occupier,)
    if property_ownership == "Tenant or landlord":
        return tenant, landlord
    if property_ownership == "Social housing":
        return (social_housing,)
    return owner_types


def _get_property_type_options(scenario):
    is_park_home = scenario.get("Park home?")
    if is_park_home is None:
        return property_types
    return (park_home,) if is_park_home else (house, bungalow, apartment_flat_or_maisonette)


def _get_park_home_main_residence_options(scenario):
    is_main_residence = scenario.get("Main residence?")
    if is_main_residence is None:
        return yes_no
    return (yes,) if is_main_residence else (no,)


def _get_council_tax_band_options(country, scenario):
    is_eligible_band = scenario.get("Eligible Council Tax band?")
    if is_eligible_band is None:
        return council_tax_bands
    if country == england:
        return (a, b, c, d) if is_eligible_band else (e, f, g, h)
    if country == scotland:
        return (a, b, c, d, e) if is_eligible_band else (f, g, h)
    if country == wales:
        return (a, b, c, d, e) if is_eligible_band else (f, g, h, i)
    return council_tax_bands


def _get_epc_rating_and_acceptance_options(scenario):
    is_abc = scenario.get("EPC A, B, C?")
    is_fg = scenario.get("EPC F or G?")
    if is_abc is None:
        return tuple(itertools.product(epc_ratings, (yes, no, i_do_not_know)))
    if is_abc:
        return (a, yes), (b, yes), (c, yes)
    if is_fg:
        return (f, yes), (g, yes)
    return ((d, yes), (e, yes)) + tuple(itertools.product(epc_ratings, (no, i_do_not_know)))


def _get_benefits_options(scenario):
    receives_benefits = scenario.get("Receiving benefits?")
    if receives_benefits is None:
        return yes_no
    return (yes,) if receives_benefits else (no,)


def _get_household_income_options(scenario):
    is_income_less_than_31k = scenario.get("Income <£31,000?")
    if is_income_less_than_31k is None:
        return household_incomes
    return (less_than_31k,) if is_income_less_than_31k else (more_than_31k,)


valid_scenario_keys = (
    "England, Scotland or Wales?",
    "Property ownership?",
    "Park home?",
    "Main residence?",
    "Eligible Council Tax band?",
    "EPC A, B, C?",
    "EPC F or G?",
    "Receiving benefits?",
    "Income <£31,000?",
)


def _validate_scenario_keys(scenario):
    for key in scenario.keys():
        if key not in valid_scenario_keys:
            raise ValueError(f'"{key}" is not a valid scenario key.')


def _assert_eligibility(scenario, expected_eligibility):
    _validate_scenario_keys(scenario)
    combinations = itertools.product(
        _get_country_options(scenario),
        _get_own_property_options(scenario),
        _get_property_type_options(scenario),
        _get_park_home_main_residence_options(scenario),
        _get_epc_rating_and_acceptance_options(scenario),
        _get_benefits_options(scenario),
        _get_household_income_options(scenario),
    )
    for (
        country,
        own_property,
        property_type,
        park_home_main_residence,
        (epc_rating, accept_suggested_epc),
        benefits,
        household_income,
    ) in combinations:
        for council_tax_band in _get_council_tax_band_options(country, scenario):
            eligibility = calculate_eligibility(
                {
                    "country": country,
                    "own_property": own_property,
                    "property_type": property_type,
                    "park_home_main_residence": park_home_main_residence,
                    "council_tax_band": council_tax_band,
                    "epc_rating": epc_rating,
                    "accept_suggested_epc": accept_suggested_epc,
                    "benefits": benefits,
                    "household_income": household_income,
                }
            )
            assert eligibility == expected_eligibility, (
                "ELIGIBILITY SCENARIO FAILED\n"
                "\n"
                f"Country: {country}\n"
                f"Ownership: {own_property}\n"
                f"Property type: {property_type}\n"
                f"Park home main residence: {park_home_main_residence}\n"
                f"Council tax band: {council_tax_band}\n"
                f"EPC rating: {epc_rating}\n"
                f"Accept suggested EPC: {accept_suggested_epc}\n"
                f"Benefits: {benefits}\n"
                f"Household income: {household_income}\n"
                "\n"
                f"EXPECTED: {expected_eligibility}\n"
                f"ACTUAL: {eligibility}"
            )


def test_scenario_1():
    _assert_eligibility({"England, Scotland or Wales?": False}, not_eligible)


def test_scenario_2():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": True,
            "Main residence?": False,
        },
        not_eligible,
    )


def test_scenario_3():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_4():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_5():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_6():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        eligible_for_gbis,
    )


def test_scenario_7():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_8():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_9():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_10():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        eligible_for_gbis,
    )


def test_scenario_11():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_12():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_13():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        not_eligible,
    )


def test_scenario_14():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Owner occupier",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_15():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": True,
            "Main residence?": False,
        },
        not_eligible,
    )


def test_scenario_16():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_17():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_18():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        eligible_for_gbis,
    )


def test_scenario_19():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": True,
            "Main residence?": True,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_20():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_21():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": True,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        eligible_for_gbis,
    )


def test_scenario_22():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": True,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_23():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": True,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_24():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_25():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_26():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": True,
            "EPC A, B, C?": False,
            "EPC F or G?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        eligible_for_gbis,
    )


def test_scenario_27():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": True,
        },
        not_eligible,
    )


def test_scenario_28():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_29():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": True,
        },
        eligible_for_gbis_and_eco4,
    )


def test_scenario_30():
    _assert_eligibility(
        {
            "England, Scotland or Wales?": True,
            "Property ownership?": "Tenant or landlord",
            "Park home?": False,
            "Eligible Council Tax band?": False,
            "EPC A, B, C?": False,
            "Receiving benefits?": False,
            "Income <£31,000?": False,
        },
        not_eligible,
    )


def test_scenario_31():
    _assert_eligibility(
        {"England, Scotland or Wales?": True, "Property ownership?": "Social housing", "EPC A, B, C?": True},
        not_eligible,
    )


def test_scenario_32():
    _assert_eligibility(
        {"England, Scotland or Wales?": True, "Property ownership?": "Social housing", "EPC A, B, C?": False},
        eligible_for_gbis_and_eco4,
    )
