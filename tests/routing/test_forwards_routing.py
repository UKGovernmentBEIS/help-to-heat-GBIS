import pytest

from help_to_heat.frontdoor.consts import (
    address_choice_field,
    address_choice_field_enter_manually,
    address_choice_field_write_address,
    address_manual_page,
    address_page,
    address_select_choice_field,
    address_select_choice_field_enter_manually,
    address_select_choice_field_select_address,
    address_select_page,
    benefits_field,
    benefits_page,
    bulb_warning_page,
    confirm_and_submit_page,
    contact_details_page,
    council_tax_band_field,
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
    council_tax_band_field_i,
    council_tax_band_page,
    council_tax_field_bands,
    country_field,
    country_field_england,
    country_field_northern_ireland,
    country_field_scotland,
    country_field_wales,
    country_page,
    duplicate_uprn_field,
    epc_accept_suggested_epc_field,
    epc_found_field,
    epc_ineligible_page,
    epc_page,
    epc_rating_is_eligible_field,
    epc_select_choice_field,
    epc_select_choice_field_enter_manually,
    epc_select_choice_field_epc_api_fail,
    epc_select_choice_field_select_epc,
    epc_select_page,
    field_dont_know,
    field_no,
    field_yes,
    household_income_field,
    household_income_field_less_than_threshold,
    household_income_field_more_than_threshold,
    household_income_page,
    loft_access_field,
    loft_access_field_no,
    loft_access_field_yes,
    loft_access_page,
    loft_field,
    loft_field_no,
    loft_field_yes,
    loft_insulation_field,
    loft_insulation_field_dont_know,
    loft_insulation_field_less_than_threshold,
    loft_insulation_field_more_than_threshold,
    loft_insulation_page,
    loft_page,
    northern_ireland_ineligible_page,
    number_of_bedrooms_field,
    number_of_bedrooms_field_one,
    number_of_bedrooms_field_studio,
    number_of_bedrooms_field_three_or_more,
    number_of_bedrooms_field_two,
    number_of_bedrooms_page,
    own_property_field,
    own_property_field_landlord,
    own_property_field_own_property,
    own_property_field_social_housing,
    own_property_field_tenant,
    own_property_fields_non_social_housing,
    own_property_page,
    park_home_field,
    park_home_ineligible_page,
    park_home_main_residence_field,
    park_home_main_residence_page,
    park_home_page,
    property_ineligible_page,
    property_subtype_field,
    property_subtype_field_detached,
    property_subtype_field_end_terrace,
    property_subtype_field_ground_floor,
    property_subtype_field_middle_floor,
    property_subtype_field_semi_detached,
    property_subtype_field_terraced,
    property_subtype_field_top_floor,
    property_subtype_page,
    property_type_field,
    property_type_field_apartment,
    property_type_field_bungalow,
    property_type_field_house,
    property_type_field_park_home,
    property_type_page,
    referral_already_submitted_page,
    schemes_page,
    success_page,
    summary_page,
    supplier_field,
    supplier_field_british_gas,
    supplier_field_bulb,
    supplier_field_e,
    supplier_field_edf,
    supplier_field_eon_next,
    supplier_field_foxglove,
    supplier_field_octopus,
    supplier_field_ovo,
    supplier_field_scottish_power,
    supplier_field_shell,
    supplier_field_utilita,
    supplier_field_utility_warehouse,
    supplier_page,
    utility_warehouse_warning_page,
    wall_insulation_field,
    wall_insulation_field_dont_know,
    wall_insulation_field_no,
    wall_insulation_field_some,
    wall_insulation_field_yes,
    wall_insulation_page,
    wall_type_field,
    wall_type_field_cavity,
    wall_type_field_dont_know,
    wall_type_field_mix,
    wall_type_field_not_listed,
    wall_type_field_solid,
    wall_type_page,
)
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page
from tests.routing import (
    _get_flow_answers,
    flow_main,
    flow_park_home,
    flow_social_housing,
)


@pytest.mark.parametrize(
    "country, expected_next_page",
    [
        (country_field_england, supplier_page),
        (country_field_scotland, supplier_page),
        (country_field_wales, supplier_page),
        (country_field_northern_ireland, northern_ireland_ineligible_page),
    ],
)
def test_country_next_page(country, expected_next_page):
    answers = {country_field: country}
    assert get_next_page(country_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "supplier, expected_next_page",
    [
        (supplier_field_british_gas, own_property_page),
        (supplier_field_bulb, bulb_warning_page),
        (supplier_field_e, own_property_page),
        (supplier_field_edf, own_property_page),
        (supplier_field_eon_next, own_property_page),
        (supplier_field_foxglove, own_property_page),
        (supplier_field_octopus, own_property_page),
        (supplier_field_ovo, own_property_page),
        (supplier_field_scottish_power, own_property_page),
        (supplier_field_shell, own_property_page),
        (supplier_field_utilita, own_property_page),
        (supplier_field_utility_warehouse, utility_warehouse_warning_page),
    ],
)
def test_supplier_next_page(supplier, expected_next_page):
    answers = {supplier_field: supplier}
    assert get_next_page(supplier_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "own_property, expected_next_page",
    [
        (own_property_field_own_property, park_home_page),
        (own_property_field_tenant, park_home_page),
        (own_property_field_social_housing, address_page),
        (own_property_field_landlord, park_home_page),
    ],
)
def test_own_property_next_page(own_property, expected_next_page):
    answers = {own_property_field: own_property}
    assert get_next_page(own_property_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "park_home, expected_next_page",
    [
        (field_yes, park_home_main_residence_page),
        (field_no, address_page),
    ],
)
def test_park_home_next_page(park_home, expected_next_page):
    answers = {park_home_field: park_home}
    assert get_next_page(park_home_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "park_home_main_residence, expected_next_page",
    [
        (field_yes, address_page),
        (field_no, park_home_ineligible_page),
    ],
)
def test_park_home_main_residence_next_page(park_home_main_residence, expected_next_page):
    answers = {park_home_main_residence_field: park_home_main_residence}
    assert get_next_page(park_home_main_residence_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "country, expected_next_page",
    [
        (country_field_england, epc_select_page),
        (country_field_scotland, address_select_page),
        (country_field_wales, epc_select_page),
    ],
)
def test_address_write_address_next_page(country, expected_next_page):
    answers = {address_choice_field: address_choice_field_write_address, country_field: country}
    assert get_next_page(address_page, answers) == (expected_next_page, False)


def test_address_enter_manually_next_page():
    answers = {address_choice_field: address_choice_field_enter_manually}
    assert get_next_page(address_page, answers) == (address_manual_page, False)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, expected_next_page, expected_redirect",
    [
        (epc_select_choice_field_select_epc, field_no, epc_page, False),
        (epc_select_choice_field_epc_api_fail, field_no, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_no, address_manual_page, False),
        (epc_select_choice_field_select_epc, field_yes, referral_already_submitted_page, False),
        (epc_select_choice_field_epc_api_fail, field_yes, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_yes, address_manual_page, False),
    ],
)
def test_epc_select_park_home_next_page(choice, duplicate_uprn, expected_next_page, expected_redirect):
    epc_found = field_yes if choice == epc_select_choice_field_select_epc else field_no
    for own_property in own_property_fields_non_social_housing:
        answers = {
            epc_select_choice_field: choice,
            duplicate_uprn_field: duplicate_uprn,
            own_property_field: own_property,
            park_home_field: field_yes,
            epc_found_field: epc_found,
        }
        assert get_next_page(epc_select_page, answers) == (expected_next_page, expected_redirect)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, expected_next_page, expected_redirect",
    [
        (epc_select_choice_field_select_epc, field_no, council_tax_band_page, False),
        (epc_select_choice_field_epc_api_fail, field_no, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_no, address_manual_page, False),
        (epc_select_choice_field_select_epc, field_yes, referral_already_submitted_page, False),
        (epc_select_choice_field_epc_api_fail, field_yes, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_yes, address_manual_page, False),
    ],
)
def test_epc_select_not_park_home_not_already_submitted_next_page(
    choice, duplicate_uprn, expected_next_page, expected_redirect
):
    for own_property in own_property_fields_non_social_housing:
        answers = {
            epc_select_choice_field: choice,
            duplicate_uprn_field: duplicate_uprn,
            own_property_field: own_property,
            park_home_field: field_no,
        }
        assert get_next_page(epc_select_page, answers) == (expected_next_page, expected_redirect)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, expected_next_page, expected_redirect",
    [
        (epc_select_choice_field_select_epc, field_no, epc_page, False),
        (epc_select_choice_field_epc_api_fail, field_no, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_no, address_manual_page, False),
        (epc_select_choice_field_select_epc, field_yes, referral_already_submitted_page, False),
        (epc_select_choice_field_epc_api_fail, field_yes, address_select_page, True),
        (epc_select_choice_field_enter_manually, field_yes, address_manual_page, False),
    ],
)
def test_epc_select_social_housing_next_page(choice, duplicate_uprn, expected_next_page, expected_redirect):
    epc_found = field_yes if choice == epc_select_choice_field_select_epc else field_no
    answers = {
        epc_select_choice_field: choice,
        duplicate_uprn_field: duplicate_uprn,
        own_property_field: own_property_field_social_housing,
        epc_found_field: epc_found,
    }
    assert get_next_page(epc_select_page, answers) == (expected_next_page, expected_redirect)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, epc_found, expected_next_page",
    [
        (address_select_choice_field_select_address, field_yes, field_yes, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_yes, field_no, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_no, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_yes, epc_page),
        (address_select_choice_field_enter_manually, field_no, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_no, benefits_page),
        (address_select_choice_field_enter_manually, field_no, field_no, address_manual_page),
    ],
)
def test_address_select_park_home_next_page(choice, duplicate_uprn, epc_found, expected_next_page):
    for own_property in own_property_fields_non_social_housing:
        answers = {
            address_select_choice_field: choice,
            own_property_field: own_property,
            park_home_field: field_yes,
            epc_found_field: epc_found,
            duplicate_uprn_field: duplicate_uprn,
        }
        assert get_next_page(address_select_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, epc_found, expected_next_page",
    [
        (address_select_choice_field_select_address, field_yes, field_yes, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_yes, field_no, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_no, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_yes, council_tax_band_page),
        (address_select_choice_field_enter_manually, field_no, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_no, council_tax_band_page),
        (address_select_choice_field_enter_manually, field_no, field_no, address_manual_page),
    ],
)
def test_address_select_not_park_home_next_page(choice, duplicate_uprn, epc_found, expected_next_page):
    for own_property in own_property_fields_non_social_housing:
        answers = {
            address_select_choice_field: choice,
            own_property_field: own_property,
            park_home_field: field_no,
            epc_found_field: epc_found,
            duplicate_uprn_field: duplicate_uprn,
        }
        assert get_next_page(address_select_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "choice, duplicate_uprn, epc_found, expected_next_page",
    [
        (address_select_choice_field_select_address, field_yes, field_yes, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_yes, field_no, referral_already_submitted_page),
        (address_select_choice_field_enter_manually, field_yes, field_no, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_yes, epc_page),
        (address_select_choice_field_enter_manually, field_no, field_yes, address_manual_page),
        (address_select_choice_field_select_address, field_no, field_no, property_type_page),
        (address_select_choice_field_enter_manually, field_no, field_no, address_manual_page),
    ],
)
def test_address_select_social_housing_next_page(choice, duplicate_uprn, epc_found, expected_next_page):
    answers = {
        address_select_choice_field: choice,
        own_property_field: own_property_field_social_housing,
        park_home_field: field_no,
        epc_found_field: epc_found,
        duplicate_uprn_field: duplicate_uprn,
    }
    assert get_next_page(address_select_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "flow, expected_next_page",
    [
        (flow_park_home, benefits_page),
        (flow_main, council_tax_band_page),
        (flow_social_housing, property_type_page),
    ],
)
def test_address_manual_next_page(flow, expected_next_page):
    for flow_answers in _get_flow_answers(flow):
        answers = {
            **flow_answers,
            epc_found_field: field_no,
            duplicate_uprn_field: field_no
        }
        assert get_next_page(address_manual_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "flow, epc_found, expected_next_page",
    [
        (flow_park_home, field_yes, epc_page),
        (flow_park_home, field_no, benefits_page),
        (flow_main, field_yes, council_tax_band_page),
        (flow_main, field_no, council_tax_band_page),
        (flow_social_housing, field_yes, epc_page),
        (flow_social_housing, field_no, property_type_page),
    ],
)
def test_referral_already_submitted_next_page(flow, epc_found, expected_next_page):
    for flow_answers in _get_flow_answers(flow):
        answers = {**flow_answers, epc_found_field: epc_found}
        assert get_next_page(referral_already_submitted_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "epc_found, expected_next_page",
    [
        (field_yes, epc_page),
        (field_no, benefits_page),
    ],
)
def test_council_tax_band_next_page(epc_found, expected_next_page):
    for flow_answers in _get_flow_answers(flow_main):
        for council_tax_band in council_tax_field_bands:
            answers = {**flow_answers, council_tax_band_field: council_tax_band, epc_found_field: epc_found}
            assert get_next_page(council_tax_band_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "flow, eligible, expected_next_page",
    [
        (flow_park_home, True, benefits_page),
        (flow_park_home, False, epc_ineligible_page),
        (flow_main, True, benefits_page),
        (flow_main, False, epc_ineligible_page),
        (flow_social_housing, True, property_type_page),
        (flow_social_housing, False, epc_ineligible_page),
    ],
)
def test_epc_eligible_next_page(flow, eligible, expected_next_page):
    for flow_answers in _get_flow_answers(flow):
        if eligible:
            eligible_combinations_answers = [
                {epc_accept_suggested_epc_field: field_no, epc_rating_is_eligible_field: field_yes},
                {epc_accept_suggested_epc_field: field_dont_know, epc_rating_is_eligible_field: field_yes},
                {epc_accept_suggested_epc_field: field_yes, epc_rating_is_eligible_field: field_yes},
            ]
            for eligible_answers in eligible_combinations_answers:
                answers = {**eligible_answers, **flow_answers}
                assert get_next_page(epc_page, answers) == (expected_next_page, False)
        else:
            answers = {
                **flow_answers,
                epc_accept_suggested_epc_field: field_yes,
                epc_rating_is_eligible_field: field_no,
            }
            assert get_next_page(epc_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "flow, benefits, expected_next_page",
    [
        (flow_park_home, field_yes, summary_page),
        (flow_park_home, field_no, household_income_page),
        (flow_main, field_yes, property_type_page),
        (flow_main, field_no, household_income_page),
    ],
)
def test_benefits_next_page(flow, benefits, expected_next_page):
    for flow_answers in _get_flow_answers(flow):
        answers = {**flow_answers, benefits_field: benefits}
        assert get_next_page(benefits_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "household_income", [household_income_field_less_than_threshold, household_income_field_more_than_threshold]
)
def test_household_income_park_home_flow_next_page(household_income):
    for flow_answers in _get_flow_answers(flow_park_home):
        answers = {
            # required answers for eligibility calculation to conclude correctly
            **flow_answers,
            country_field: country_field_england,
            household_income_field: household_income,
            property_type_field: property_type_field_park_home,
            park_home_main_residence_field: field_yes,
        }
        assert get_next_page(household_income_page, answers) == (summary_page, False)


eligible_council_tax_bands_england = [
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
]
ineligible_council_tax_bands_england = [
    council_tax_band_field_e,
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
]
eligible_council_tax_bands_scotland = [
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
]
ineligible_council_tax_bands_scotland = [council_tax_band_field_f, council_tax_band_field_g, council_tax_band_field_h]
eligible_council_tax_bands_wales = [
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
]
ineligible_council_tax_bands_wales = [
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
    council_tax_band_field_i,
]


@pytest.mark.parametrize(
    "household_income, country, council_tax_bands, expected_next_page",
    [
        (
            household_income_field_less_than_threshold,
            country_field_england,
            eligible_council_tax_bands_england,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_england,
            eligible_council_tax_bands_england,
            property_type_page,
        ),
        (
            household_income_field_less_than_threshold,
            country_field_england,
            ineligible_council_tax_bands_england,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_england,
            ineligible_council_tax_bands_england,
            property_ineligible_page,
        ),
        (
            household_income_field_less_than_threshold,
            country_field_scotland,
            eligible_council_tax_bands_scotland,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_scotland,
            eligible_council_tax_bands_scotland,
            property_type_page,
        ),
        (
            household_income_field_less_than_threshold,
            country_field_scotland,
            ineligible_council_tax_bands_scotland,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_scotland,
            ineligible_council_tax_bands_scotland,
            property_ineligible_page,
        ),
        (
            household_income_field_less_than_threshold,
            country_field_wales,
            eligible_council_tax_bands_wales,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_wales,
            eligible_council_tax_bands_wales,
            property_type_page,
        ),
        (
            household_income_field_less_than_threshold,
            country_field_wales,
            ineligible_council_tax_bands_wales,
            property_type_page,
        ),
        (
            household_income_field_more_than_threshold,
            country_field_wales,
            ineligible_council_tax_bands_wales,
            property_ineligible_page,
        ),
    ],
)
def test_household_income_main_flow_next_page(household_income, country, council_tax_bands, expected_next_page):
    for flow_answers in _get_flow_answers(flow_main):
        for council_tax_band in council_tax_bands:
            answers = {
                **flow_answers,
                country_field: country,
                council_tax_band_field: council_tax_band,
                household_income_field: household_income,
            }
            assert get_next_page(household_income_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "property_type", [property_type_field_house, property_type_field_bungalow, property_type_field_apartment]
)
def test_property_type_next_page(property_type):
    answers = {property_type_field: property_type}
    assert get_next_page(property_type_page, answers) == (property_subtype_page, False)


@pytest.mark.parametrize(
    "property_subtype",
    [
        property_subtype_field_top_floor,
        property_subtype_field_middle_floor,
        property_subtype_field_ground_floor,
        property_subtype_field_detached,
        property_subtype_field_semi_detached,
        property_subtype_field_terraced,
        property_subtype_field_end_terrace,
    ],
)
def test_property_subtype_next_page(property_subtype):
    answers = {property_subtype_field: property_subtype}
    assert get_next_page(property_subtype_page, answers) == (number_of_bedrooms_page, False)


@pytest.mark.parametrize(
    "number_of_bedrooms",
    [
        number_of_bedrooms_field_studio,
        number_of_bedrooms_field_one,
        number_of_bedrooms_field_two,
        number_of_bedrooms_field_three_or_more,
    ],
)
def test_number_of_bedrooms_next_page(number_of_bedrooms):
    answers = {number_of_bedrooms_field: number_of_bedrooms}
    assert get_next_page(number_of_bedrooms_page, answers) == (wall_type_page, False)


@pytest.mark.parametrize(
    "wall_type",
    [
        wall_type_field_solid,
        wall_type_field_cavity,
        wall_type_field_mix,
        wall_type_field_not_listed,
        wall_type_field_dont_know,
    ],
)
def test_wall_type_next_page(wall_type):
    answers = {wall_type_field: wall_type}
    assert get_next_page(wall_type_page, answers) == (wall_insulation_page, False)


@pytest.mark.parametrize(
    "wall_insulation",
    [
        wall_insulation_field_yes,
        wall_insulation_field_some,
        wall_insulation_field_no,
        wall_insulation_field_dont_know,
    ],
)
def test_wall_insulation_next_page(wall_insulation):
    answers = {wall_insulation_field: wall_insulation}
    assert get_next_page(wall_insulation_page, answers) == (loft_page, False)


@pytest.mark.parametrize(
    "loft, expected_next_page",
    [
        (loft_field_yes, loft_access_page),
        (loft_field_no, summary_page),
    ],
)
def test_loft_next_page(loft, expected_next_page):
    answers = {loft_field: loft}
    assert get_next_page(loft_page, answers) == (expected_next_page, False)


@pytest.mark.parametrize(
    "loft_access",
    [
        loft_access_field_yes,
        loft_access_field_no,
    ],
)
def test_loft_access_next_page(loft_access):
    answers = {loft_access_field: loft_access}
    assert get_next_page(loft_access_page, answers) == (loft_insulation_page, False)


@pytest.mark.parametrize(
    "loft_insulation",
    [
        loft_insulation_field_more_than_threshold,
        loft_insulation_field_less_than_threshold,
        loft_insulation_field_dont_know,
    ],
)
def test_loft_insulation_next_page(loft_insulation):
    answers = {loft_insulation_field: loft_insulation}
    assert get_next_page(loft_insulation_page, answers) == (summary_page, False)


def test_summary_next_page():
    assert get_next_page(summary_page, {}) == (schemes_page, False)


def test_schemes_next_page():
    assert get_next_page(schemes_page, {}) == (contact_details_page, False)


def test_contact_details_next_page():
    assert get_next_page(contact_details_page, {}) == (confirm_and_submit_page, False)


def test_confirm_and_submit_page():
    assert get_next_page(confirm_and_submit_page, {}) == (success_page, False)
