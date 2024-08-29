import pytest

from help_to_heat.frontdoor.consts import (
    address_choice_field,
    address_choice_field_enter_manually,
    address_choice_field_epc_api_fail,
    address_choice_field_write_address,
    address_manual_page,
    address_page,
    address_select_choice_field,
    address_select_choice_field_enter_manually,
    address_select_page,
    benefits_field,
    benefits_page,
    bulb_warning_page,
    bulb_warning_page_field,
    confirm_and_submit_page,
    contact_details_page,
    council_tax_band_field,
    council_tax_band_page,
    country_field,
    country_field_england,
    country_field_northern_ireland,
    country_field_scotland,
    country_field_wales,
    country_page,
    duplicate_uprn_field,
    epc_accept_suggested_epc_field,
    epc_ineligible_page,
    epc_page,
    epc_rating_is_eligible_field,
    epc_select_choice_field,
    epc_select_choice_field_enter_manually,
    epc_select_choice_field_epc_api_fail,
    epc_select_page,
    field_no,
    field_yes,
    govuk_start_page,
    household_income_field,
    household_income_field_more_than_threshold,
    household_income_page,
    loft_access_page,
    loft_insulation_page,
    loft_page,
    northern_ireland_ineligible_page,
    number_of_bedrooms_page,
    own_property_page,
    park_home_ineligible_page,
    park_home_main_residence_field,
    park_home_main_residence_page,
    park_home_page,
    property_ineligible_page,
    property_subtype_page,
    property_type_page,
    referral_already_submitted_page,
    schemes_page,
    shell_warning_page,
    shell_warning_page_field,
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
    utility_warehouse_warning_page_field,
    wall_insulation_page,
    wall_type_page,
)
from help_to_heat.frontdoor.routing.backwards_routing import get_prev_page
from tests.routing import (
    address_flow_manually,
    address_flow_write_address_epc_api_fail_manually,
    address_flow_write_address_epc_api_fail_select,
    address_flow_write_address_epc_hit_select,
    address_flow_write_address_epc_hit_write_manually,
    address_flow_write_address_scotland_manually,
    address_flow_write_address_scotland_select_epc,
    address_flow_write_address_scotland_select_no_epc,
    circumstances_flow_benefits_eligible,
    circumstances_flow_income_eligible,
    get_address_answers,
    get_circumstances_answers,
    get_council_tax_band_answers,
    get_country_answers,
    get_epc_answers,
    get_loft_access_answers,
    get_loft_answers,
    get_loft_insulation_answers,
    get_number_of_bedrooms_answers,
    get_property_flow_answers,
    get_property_type_answers,
    get_summary_answers,
    get_wall_insulation_answers,
    get_wall_type_answers,
    ineligible_council_tax_bands_england,
    ineligible_council_tax_bands_scotland,
    ineligible_council_tax_bands_wales,
    loft_flow_no,
    loft_flow_yes,
    property_flow_main,
    property_flow_park_home,
    property_flow_social_housing,
)


def test_country_prev_page():
    assert get_prev_page(country_page, {}) == govuk_start_page


def test_supplier_prev_page():
    for answers in get_country_answers():
        assert get_prev_page(supplier_page, answers) == country_page


def test_northern_ireland_ineligible_prev_page():
    answers = {country_field: country_field_northern_ireland}
    assert get_prev_page(northern_ireland_ineligible_page, answers) == country_page


def test_bulb_warning_page_prev_page():
    for flow_answers in get_country_answers():
        answers = {**flow_answers, supplier_field: supplier_field_bulb, bulb_warning_page_field: field_yes}
        assert get_prev_page(bulb_warning_page, answers) == supplier_page


def test_shell_warning_page_prev_page():
    for flow_answers in get_country_answers():
        answers = {**flow_answers, supplier_field: supplier_field_shell, shell_warning_page_field: field_yes}
        assert get_prev_page(shell_warning_page, answers) == supplier_page


def test_utility_warehouse_warning_prev_page():
    for flow_answers in get_country_answers():
        answers = {
            **flow_answers,
            supplier_field: supplier_field_utility_warehouse,
            utility_warehouse_warning_page_field: field_yes,
        }
        assert get_prev_page(utility_warehouse_warning_page, answers) == supplier_page


@pytest.mark.parametrize(
    "supplier, expected_prev_page",
    [
        (supplier_field_british_gas, supplier_page),
        (supplier_field_bulb, bulb_warning_page),
        (supplier_field_e, supplier_page),
        (supplier_field_edf, supplier_page),
        (supplier_field_eon_next, supplier_page),
        (supplier_field_foxglove, supplier_page),
        (supplier_field_octopus, supplier_page),
        (supplier_field_ovo, supplier_page),
        (supplier_field_scottish_power, supplier_page),
        (supplier_field_shell, shell_warning_page),
        (supplier_field_utilita, supplier_page),
        (supplier_field_utility_warehouse, utility_warehouse_warning_page),
    ],
)
def test_own_property_prev_page(supplier, expected_prev_page):
    for flow_answers in get_country_answers():
        answers = {**flow_answers, supplier_field: supplier}

        if supplier == supplier_field_bulb:
            answers[bulb_warning_page_field] = field_yes

        if supplier == supplier_field_shell:
            answers[shell_warning_page_field] = field_yes

        if supplier == supplier_field_utility_warehouse:
            answers[utility_warehouse_warning_page_field] = field_yes

        assert get_prev_page(own_property_page, answers) == expected_prev_page


def test_park_home_prev_page():
    for flow_answers in get_property_flow_answers(property_flow_park_home):
        assert get_prev_page(park_home_page, flow_answers) == own_property_page


def test_park_home_main_residence_prev_page():
    for flow_answers in get_property_flow_answers(property_flow_park_home):
        assert get_prev_page(park_home_main_residence_page, flow_answers) == park_home_page


def test_park_home_ineligible_prev_page():
    for flow_answers in get_property_flow_answers(property_flow_park_home):
        answers = {**flow_answers, park_home_main_residence_field: field_no}
        assert get_prev_page(park_home_ineligible_page, answers) == park_home_main_residence_page


@pytest.mark.parametrize(
    "flow, expected_prev_page",
    [
        (property_flow_park_home, park_home_main_residence_page),
        (property_flow_main, park_home_page),
        (property_flow_social_housing, own_property_page),
    ],
)
def test_address_page_prev_page(flow, expected_prev_page):
    for flow_answers in get_property_flow_answers(flow):
        assert get_prev_page(address_page, flow_answers) == expected_prev_page


def test_epc_select_prev_page():
    for flow_answers in get_property_flow_answers():
        country = flow_answers.get(country_field)
        if country != country_field_scotland:
            answers = {**flow_answers, address_choice_field: address_choice_field_write_address}
            assert get_prev_page(epc_select_page, answers) == address_page


def test_address_select_prev_page():
    for flow_answers in get_property_flow_answers():
        country = flow_answers[country_field]
        if country in [country_field_england, country_field_wales]:
            answers = {**flow_answers, address_choice_field: address_choice_field_epc_api_fail}
            assert get_prev_page(address_select_page, answers) == address_page
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
            }
            assert get_prev_page(address_select_page, answers) == epc_select_page

        if country == country_field_scotland:
            answers = {**flow_answers, address_choice_field: address_choice_field_write_address}
            assert get_prev_page(address_select_page, answers) == address_page


def test_address_manual_from_address_page_prev_page():
    for flow_answers in get_property_flow_answers():
        answers = {
            **flow_answers,
            address_choice_field: address_choice_field_enter_manually,
        }

        assert get_prev_page(address_manual_page, answers) == address_page


def test_address_manual_from_epc_select_page_prev_page():
    for flow_answers in get_property_flow_answers():
        country = flow_answers.get(country_field)
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually,
            }
            assert get_prev_page(address_manual_page, answers) == epc_select_page


def test_address_manual_from_address_select_page_prev_page():
    for flow_answers in get_property_flow_answers():
        country = flow_answers.get(country_field)
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually,
            }
            assert get_prev_page(address_manual_page, answers) == address_select_page

        if country == country_field_scotland:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_enter_manually,
            }
            assert get_prev_page(address_manual_page, answers) == address_select_page


@pytest.mark.parametrize(
    "address_flow, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, epc_select_page),
        (address_flow_write_address_epc_api_fail_select, address_select_page),
        (address_flow_write_address_scotland_select_epc, address_select_page),
        (address_flow_write_address_scotland_select_no_epc, address_select_page),
    ],
)
def test_referral_already_submitted_page_prev_page(address_flow, expected_prev_page):
    for flow_answers in get_address_answers(address_flow):
        answers = {**flow_answers, duplicate_uprn_field: field_yes}

        assert get_prev_page(referral_already_submitted_page, answers) == expected_prev_page


@pytest.mark.parametrize(
    "address_flow, duplicate_uprn, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, field_no, epc_select_page),
        (address_flow_write_address_epc_hit_select, field_yes, referral_already_submitted_page),
        (address_flow_write_address_epc_hit_write_manually, field_no, address_manual_page),
        (address_flow_write_address_epc_hit_write_manually, field_yes, address_manual_page),
        (address_flow_write_address_epc_api_fail_select, field_no, address_select_page),
        (address_flow_write_address_epc_api_fail_select, field_yes, referral_already_submitted_page),
        (address_flow_write_address_epc_api_fail_manually, field_no, address_manual_page),
        (address_flow_write_address_epc_api_fail_manually, field_yes, address_manual_page),
        (address_flow_write_address_scotland_select_epc, field_no, address_select_page),
        (address_flow_write_address_scotland_select_epc, field_yes, referral_already_submitted_page),
        (address_flow_write_address_scotland_select_no_epc, field_no, address_select_page),
        (address_flow_write_address_scotland_select_no_epc, field_yes, referral_already_submitted_page),
        (address_flow_write_address_scotland_manually, field_no, address_manual_page),
        (address_flow_write_address_scotland_manually, field_yes, address_manual_page),
        (address_flow_manually, field_no, address_manual_page),
        (address_flow_manually, field_yes, address_manual_page),
    ],
)
def test_council_tax_band_prev_page(address_flow, duplicate_uprn, expected_prev_page):
    for flow_answers in get_address_answers(
        address_flow, duplicate_uprn=duplicate_uprn, property_flow=property_flow_main
    ):
        assert get_prev_page(council_tax_band_page, flow_answers) == expected_prev_page


@pytest.mark.parametrize(
    "address_flow, property_flow, duplicate_uprn, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, property_flow_park_home, field_no, epc_select_page),
        (
            address_flow_write_address_epc_hit_select,
            property_flow_park_home,
            field_yes,
            referral_already_submitted_page,
        ),
        (address_flow_write_address_epc_hit_select, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_epc_hit_select, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_epc_hit_select, property_flow_social_housing, field_no, epc_select_page),
        (
            address_flow_write_address_epc_hit_select,
            property_flow_social_housing,
            field_yes,
            referral_already_submitted_page,
        ),
        (address_flow_write_address_scotland_select_epc, property_flow_park_home, field_no, address_select_page),
        (
            address_flow_write_address_scotland_select_epc,
            property_flow_park_home,
            field_yes,
            referral_already_submitted_page,
        ),
        (address_flow_write_address_scotland_select_epc, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_scotland_select_epc, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_scotland_select_epc, property_flow_social_housing, field_no, address_select_page),
        (
            address_flow_write_address_scotland_select_epc,
            property_flow_social_housing,
            field_yes,
            referral_already_submitted_page,
        ),
    ],
)
def test_epc_prev_page(address_flow, property_flow, duplicate_uprn, expected_prev_page):
    for flow_answers in get_council_tax_band_answers(address_flow, duplicate_uprn, property_flow):
        assert get_prev_page(epc_page, flow_answers) == expected_prev_page


@pytest.mark.parametrize(
    "address_flow, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, epc_page),
        (address_flow_write_address_scotland_select_epc, epc_page),
    ],
)
def test_epc_ineligible_prev_page(address_flow, expected_prev_page):
    for flow_answers in get_council_tax_band_answers(address_flow):
        answers = {
            **flow_answers,
            epc_accept_suggested_epc_field: field_yes,
            epc_rating_is_eligible_field: field_no,
        }
        assert get_prev_page(epc_ineligible_page, answers) == expected_prev_page


@pytest.mark.parametrize(
    "address_flow, property_flow, duplicate_uprn, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, property_flow_park_home, field_no, epc_page),
        (address_flow_write_address_epc_hit_select, property_flow_park_home, field_yes, epc_page),
        (address_flow_write_address_epc_hit_select, property_flow_main, field_no, epc_page),
        (address_flow_write_address_epc_hit_select, property_flow_main, field_yes, epc_page),
        (address_flow_write_address_epc_hit_write_manually, property_flow_park_home, field_no, address_manual_page),
        (address_flow_write_address_epc_hit_write_manually, property_flow_park_home, field_yes, address_manual_page),
        (address_flow_write_address_epc_hit_write_manually, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_epc_hit_write_manually, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_epc_api_fail_select, property_flow_park_home, field_no, address_select_page),
        (
            address_flow_write_address_epc_api_fail_select,
            property_flow_park_home,
            field_yes,
            referral_already_submitted_page,
        ),
        (address_flow_write_address_epc_api_fail_select, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_epc_api_fail_select, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_epc_api_fail_manually, property_flow_park_home, field_no, address_manual_page),
        (address_flow_write_address_epc_api_fail_manually, property_flow_park_home, field_yes, address_manual_page),
        (address_flow_write_address_epc_api_fail_manually, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_epc_api_fail_manually, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_scotland_select_epc, property_flow_park_home, field_no, epc_page),
        (address_flow_write_address_scotland_select_epc, property_flow_park_home, field_yes, epc_page),
        (address_flow_write_address_scotland_select_epc, property_flow_main, field_no, epc_page),
        (address_flow_write_address_scotland_select_epc, property_flow_main, field_yes, epc_page),
        (address_flow_write_address_scotland_select_no_epc, property_flow_park_home, field_no, address_select_page),
        (
            address_flow_write_address_scotland_select_no_epc,
            property_flow_park_home,
            field_yes,
            referral_already_submitted_page,
        ),
        (address_flow_write_address_scotland_select_no_epc, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_scotland_select_no_epc, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_write_address_scotland_manually, property_flow_park_home, field_no, address_manual_page),
        (address_flow_write_address_scotland_manually, property_flow_park_home, field_yes, address_manual_page),
        (address_flow_write_address_scotland_manually, property_flow_main, field_no, council_tax_band_page),
        (address_flow_write_address_scotland_manually, property_flow_main, field_yes, council_tax_band_page),
        (address_flow_manually, property_flow_park_home, field_no, address_manual_page),
        (address_flow_manually, property_flow_park_home, field_yes, address_manual_page),
        (address_flow_manually, property_flow_main, field_no, council_tax_band_page),
        (address_flow_manually, property_flow_main, field_yes, council_tax_band_page),
    ],
)
def test_benefits_prev_page(address_flow, property_flow, duplicate_uprn, expected_prev_page):
    for flow_answers in get_epc_answers(address_flow, duplicate_uprn, property_flow):
        assert get_prev_page(benefits_page, flow_answers) == expected_prev_page


@pytest.mark.parametrize("property_flow", [property_flow_park_home, property_flow_main])
def test_household_income_prev_page(property_flow):
    for flow_answers in get_epc_answers(property_flow=property_flow):
        answers = {**flow_answers, benefits_field: field_no}
        assert get_prev_page(household_income_page, answers) == benefits_page


@pytest.mark.parametrize(
    "country, ineligible_bands",
    [
        (country_field_england, ineligible_council_tax_bands_england),
        (country_field_scotland, ineligible_council_tax_bands_scotland),
        (country_field_wales, ineligible_council_tax_bands_wales),
    ],
)
def test_property_ineligible_prev_page(country, ineligible_bands):
    for flow_answers in get_epc_answers(property_flow=property_flow_main):
        flow_country = flow_answers.get(country_field)
        if flow_country == country:
            for council_tax_band in ineligible_bands:
                answers = {
                    **flow_answers,
                    benefits_field: field_no,
                    household_income_field: household_income_field_more_than_threshold,
                    council_tax_band_field: council_tax_band,
                }
                assert get_prev_page(property_ineligible_page, answers) == household_income_page


@pytest.mark.parametrize(
    "circumstances_flow, expected_prev_page",
    [
        (circumstances_flow_benefits_eligible, benefits_page),
        (circumstances_flow_income_eligible, household_income_page),
    ],
)
def test_property_type_main_flow_prev_page(circumstances_flow, expected_prev_page):
    for flow_answers in get_circumstances_answers(
        circumstances_flow=circumstances_flow, property_flow=property_flow_main
    ):
        assert get_prev_page(property_type_page, flow_answers) == expected_prev_page


@pytest.mark.parametrize(
    "address_flow, duplicate_uprn, expected_prev_page",
    [
        (address_flow_write_address_epc_hit_select, field_no, epc_page),
        (address_flow_write_address_epc_hit_select, field_yes, epc_page),
        (address_flow_write_address_epc_hit_write_manually, field_no, address_manual_page),
        (address_flow_write_address_epc_hit_write_manually, field_yes, address_manual_page),
        (address_flow_write_address_epc_api_fail_select, field_no, address_select_page),
        (address_flow_write_address_epc_api_fail_select, field_yes, referral_already_submitted_page),
        (address_flow_write_address_epc_api_fail_manually, field_no, address_manual_page),
        (address_flow_write_address_epc_api_fail_manually, field_yes, address_manual_page),
        (address_flow_write_address_scotland_select_epc, field_no, epc_page),
        (address_flow_write_address_scotland_select_epc, field_yes, epc_page),
        (address_flow_write_address_scotland_select_no_epc, field_no, address_select_page),
        (address_flow_write_address_scotland_select_no_epc, field_yes, referral_already_submitted_page),
        (address_flow_write_address_scotland_manually, field_no, address_manual_page),
        (address_flow_write_address_scotland_manually, field_yes, address_manual_page),
        (address_flow_manually, field_no, address_manual_page),
        (address_flow_manually, field_yes, address_manual_page),
    ],
)
def test_property_type_social_housing_prev_page(address_flow, duplicate_uprn, expected_prev_page):
    for flow_answers in get_circumstances_answers(
        address_flow=address_flow, duplicate_uprn=duplicate_uprn, property_flow=property_flow_social_housing
    ):
        assert get_prev_page(property_type_page, flow_answers) == expected_prev_page


def test_property_subtype_prev_page():
    for flow_answers in get_property_type_answers():
        assert get_prev_page(property_subtype_page, flow_answers) == property_type_page


def test_number_of_bedrooms_prev_page():
    for flow_answers in get_number_of_bedrooms_answers():
        assert get_prev_page(number_of_bedrooms_page, flow_answers) == property_subtype_page


def test_wall_type_prev_page():
    for flow_answers in get_wall_type_answers():
        assert get_prev_page(wall_type_page, flow_answers) == number_of_bedrooms_page


def test_wall_insulation_prev_page():
    for flow_answers in get_wall_insulation_answers():
        assert get_prev_page(wall_insulation_page, flow_answers) == wall_type_page


def test_loft_prev_page():
    for flow_answers in get_loft_answers():
        assert get_prev_page(loft_page, flow_answers) == wall_insulation_page


def test_loft_access_prev_page():
    for flow_answers in get_loft_access_answers():
        assert get_prev_page(loft_access_page, flow_answers) == loft_page


def test_loft_insulation_prev_page():
    for flow_answers in get_loft_insulation_answers():
        assert get_prev_page(loft_insulation_page, flow_answers) == loft_access_page


@pytest.mark.parametrize(
    "circumstances_flow, expected_prev_page",
    [
        (circumstances_flow_benefits_eligible, benefits_page),
        (circumstances_flow_income_eligible, household_income_page),
    ],
)
def test_summary_park_home_prev_page(circumstances_flow, expected_prev_page):
    for flow_answers in get_circumstances_answers(
        circumstances_flow=circumstances_flow, property_flow=property_flow_park_home
    ):
        assert get_prev_page(summary_page, flow_answers) == expected_prev_page


@pytest.mark.parametrize(
    "loft_flow, expected_prev_page",
    [
        (loft_flow_yes, loft_insulation_page),
        (loft_flow_no, loft_page),
    ],
)
def test_summary_other_flows_prev_page(loft_flow, expected_prev_page):
    if loft_flow == loft_flow_yes:
        flow_answers = get_loft_insulation_answers()
    else:
        flow_answers = get_loft_answers(loft_flow)

    for answers in flow_answers:
        assert get_prev_page(summary_page, answers) == expected_prev_page


def test_schemes_prev_page():
    for flow_answers in get_summary_answers():
        assert get_prev_page(schemes_page, flow_answers) == summary_page


def test_contact_details_prev_page():
    for flow_answers in get_summary_answers():
        assert get_prev_page(contact_details_page, flow_answers) == schemes_page


def test_confirm_and_submit_prev_page():
    for flow_answers in get_summary_answers():
        assert get_prev_page(confirm_and_submit_page, flow_answers) == contact_details_page
