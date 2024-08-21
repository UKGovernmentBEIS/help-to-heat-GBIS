import pytest

from help_to_heat.frontdoor.routing.backwards_routing import get_prev_page
from help_to_heat.frontdoor.consts import *
from tests.routing import get_country_answers, property_flow_park_home, property_flow_main, \
    property_flow_social_housing, \
    all_property_flows, get_all_property_flow_answers, address_flow_write_address_epc_hit_select, \
    address_flow_write_address_epc_api_fail_select, address_flow_write_address_scotland_select_epc, \
    address_flow_write_address_scotland_select_no_epc, get_address_answers, get_property_flow_answers, \
    address_flow_write_address_epc_hit_write_manually, address_flow_write_address_epc_api_fail_manually, \
    address_flow_write_address_scotland_manually, address_flow_manually, get_council_tax_band_answers


def test_country_prev_page():
    assert get_prev_page(country_page, {}) == govuk_start_page


def test_supplier_prev_page():
    assert get_prev_page(supplier_page, {}) == country_page


def test_northern_ireland_ineligible_prev_page():
    assert get_prev_page(northern_ireland_ineligible_page, {}) == country_page


def test_bulb_warning_page_prev_page():
    assert get_prev_page(bulb_warning_page, {}) == supplier_page


def test_utility_warehouse_warning_prev_page():
    assert get_prev_page(utility_warehouse_warning_page, {}) == supplier_page


@pytest.mark.parametrize("supplier, expected_prev_page", [
    (supplier_field_british_gas, supplier_page),
    (supplier_field_bulb, bulb_warning_page),
    (supplier_field_e, supplier_page),
    (supplier_field_edf, supplier_page),
    (supplier_field_eon_next, supplier_page),
    (supplier_field_foxglove, supplier_page),
    (supplier_field_octopus, supplier_page),
    (supplier_field_ovo, supplier_page),
    (supplier_field_scottish_power, supplier_page),
    (supplier_field_shell, supplier_page),
    (supplier_field_utilita, supplier_page),
    (supplier_field_utility_warehouse, utility_warehouse_warning_page),
])
def test_own_property_prev_page(supplier, expected_prev_page):
    for flow_answers in get_country_answers():
        answers = {
            **flow_answers,
            supplier_field: supplier
        }

        if supplier == supplier_field_bulb:
            answers[bulb_warning_page_field] = field_yes

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
        answers = {
            **flow_answers,
            park_home_main_residence_field: field_no
        }
        assert get_prev_page(park_home_ineligible_page, answers) == park_home_page


@pytest.mark.parametrize("flow, expected_prev_page", [
    (property_flow_park_home, park_home_main_residence_page),
    (property_flow_main, park_home_page),
    (property_flow_social_housing, own_property_page)
])
def test_address_page_prev_page(flow, expected_prev_page):
    for flow_answers in get_property_flow_answers(flow):
        assert get_prev_page(address_page, flow_answers) == expected_prev_page


def test_epc_select_prev_page():
    for flow_answers in get_all_property_flow_answers():
        answers = {
            **flow_answers,
            address_choice_field: address_choice_field_write_address
        }
        assert get_prev_page(epc_select_page, answers) == address_page


def test_address_select_prev_page():
    for flow_answers in get_all_property_flow_answers():
        country = flow_answers[country_field]
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail
            }
            assert get_prev_page(address_select_page, answers) == address_page

        if country == country_field_scotland:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address
            }
            assert get_prev_page(address_select_page, answers) == address_page


def test_address_manual_from_address_page_prev_page():
    for flow_answers in get_all_property_flow_answers():
        answers = {
            **flow_answers,
            address_choice_field: address_choice_field_enter_manually,
        }

        assert get_prev_page(address_manual_page, answers) == address_page


def test_address_manual_from_epc_select_page_prev_page():
    for flow_answers in get_all_property_flow_answers():
        country = flow_answers[country_field]
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually
            }
            assert get_prev_page(address_manual_page, answers) == address_page


def test_address_manual_from_address_select_page_prev_page():
    for flow_answers in get_all_property_flow_answers():
        country = flow_answers[country_field]
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually
            }
            assert get_prev_page(address_manual_page, answers) == address_page

        if country == country_field_scotland:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_enter_manually
            }
            assert get_prev_page(address_select_page, answers) == address_page


@pytest.mark.parametrize("address_flow, expected_prev_page", [
    (address_flow_write_address_epc_hit_select, epc_select_page),
    (address_flow_write_address_epc_api_fail_select, address_select_page),
    (address_flow_write_address_scotland_select_epc, address_select_page),
    (address_flow_write_address_scotland_select_no_epc, address_select_page),
])
def test_referral_already_submitted_page_prev_page(address_flow, expected_prev_page):
    for address_answers in get_address_answers(address_flow):
        answers = {
            **address_answers,
            duplicate_uprn_field: field_yes
        }

        assert get_prev_page(referral_already_submitted_page, answers) == expected_prev_page


@pytest.mark.parametrize("address_flow, expected_prev_page", [
    (address_flow_write_address_epc_hit_select, epc_select_page),
    (address_flow_write_address_epc_hit_write_manually, address_manual_page),
    (address_flow_write_address_epc_api_fail_select, address_select_page),
    (address_flow_write_address_epc_api_fail_manually, address_manual_page),
    (address_flow_write_address_scotland_select_epc, address_select_page),
    (address_flow_write_address_scotland_select_no_epc, address_manual_page),
    (address_flow_write_address_scotland_manually, address_manual_page),
    (address_flow_manually, address_manual_page),
])
def test_council_tax_band_prev_page(address_flow, expected_prev_page):
    for address_answers in get_address_answers(address_flow, duplicate_uprn=None, property_flow=property_flow_main):
        assert get_prev_page(council_tax_band_page, address_answers) == expected_prev_page


@pytest.mark.parametrize("address_flow, property_flow, duplicate_uprn, expected_prev_page", [
    (address_flow_write_address_epc_hit_select, property_flow_park_home, field_yes, epc_select_page),
    (address_flow_write_address_scotland_select_epc, property_flow_park_home, field_yes, address_select_page),
    (address_flow_write_address_epc_hit_select, property_flow_main, field_yes, council_tax_band_page),
    (address_flow_write_address_scotland_select_epc, property_flow_main, field_yes, council_tax_band_page),
    (address_flow_write_address_epc_hit_select, property_flow_social_housing, field_yes, epc_select_page),
    (address_flow_write_address_scotland_select_epc, property_flow_social_housing, field_yes, address_select_page),
    (address_flow_write_address_epc_hit_select, property_flow_park_home, field_no, duplicate_uprn_field),
    (address_flow_write_address_scotland_select_epc, property_flow_park_home, field_no, duplicate_uprn_field),
    (address_flow_write_address_epc_hit_select, property_flow_main, field_no, council_tax_band_page),
    (address_flow_write_address_scotland_select_epc, property_flow_main, field_no, council_tax_band_page),
    (address_flow_write_address_epc_hit_select, property_flow_social_housing, field_no, duplicate_uprn_field),
    (address_flow_write_address_scotland_select_epc, property_flow_social_housing, field_no, duplicate_uprn_field),
])
def test_epc_prev_page(address_flow, property_flow, duplicate_uprn, expected_prev_page):
    for council_tax_band_answers in get_council_tax_band_answers(address_flow, duplicate_uprn, property_flow):
        assert get_prev_page(epc_page, council_tax_band_answers) == expected_prev_page


@pytest.mark.parametrize("address_flow, expected_prev_page", [
    (address_flow_write_address_epc_hit_select, epc_page),
    (address_flow_write_address_scotland_select_epc, epc_page),
])
def test_epc_ineligible_prev_page(address_flow, expected_prev_page):
    for council_tax_band_answers in get_council_tax_band_answers(address_flow):
        answers = {
            **council_tax_band_answers,
            epc_accept_suggested_epc_field: field_yes,
            epc_rating_is_eligible_field: field_no
        }
        assert get_prev_page(epc_ineligible_page, answers) == expected_prev_page
