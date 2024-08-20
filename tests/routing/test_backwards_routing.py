import pytest

from help_to_heat.frontdoor.routing.backwards_routing import get_prev_page
from help_to_heat.frontdoor.consts import *
from tests.routing import get_country_answers, get_flow_answers, flow_park_home, flow_main, flow_social_housing, \
    all_flows, get_all_flow_answers


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
    for flow_answers in get_flow_answers(flow_park_home):
        assert get_prev_page(park_home_page, flow_answers) == own_property_page


def test_park_home_main_residence_prev_page():
    for flow_answers in get_flow_answers(flow_park_home):
        assert get_prev_page(park_home_main_residence_page, flow_answers) == park_home_page


def test_park_home_ineligible_prev_page():
    for flow_answers in get_flow_answers(flow_park_home):
        answers = {
            **flow_answers,
            park_home_main_residence_field: field_no
        }
        assert get_prev_page(park_home_ineligible_page, answers) == park_home_page


@pytest.mark.parametrize("flow, expected_prev_page", [
    (flow_park_home, park_home_main_residence_page),
    (flow_main, park_home_page),
    (flow_social_housing, own_property_page)
])
def test_address_page_prev_page(flow, expected_prev_page):
    for flow_answers in get_flow_answers(flow):
        assert get_prev_page(address_page, flow_answers) == expected_prev_page


def test_epc_select_prev_page():
    for flow_answers in get_all_flow_answers():
        answers = {
            **flow_answers,
            address_choice_field: address_choice_field_write_address
        }
        assert get_prev_page(epc_select_page, answers) == address_page


def test_address_select_prev_page():
    for flow_answers in get_all_flow_answers():
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
    for flow_answers in get_all_flow_answers():
        answers = {
            **flow_answers,
            address_choice_field: address_choice_field_enter_manually,
        }

        assert get_prev_page(address_manual_page, answers) == address_page


def test_address_manual_from_epc_select_page_prev_page():
    for flow_answers in get_all_flow_answers():
        country = flow_answers[country_field]
        if country in [country_field_england, country_field_wales]:
            answers = {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually
            }
            assert get_prev_page(address_manual_page, answers) == address_page


def test_address_manual_from_address_select_page_prev_page():
    for flow_answers in get_all_flow_answers():
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
