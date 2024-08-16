import pytest

from help_to_heat.frontdoor.routing.backwards_routing import get_prev_page
from help_to_heat.frontdoor.consts import *


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
    answers = {
        supplier_field: supplier
    }

    if supplier == supplier_field_bulb:
        answers[bulb_warning_page_field] = field_yes

    if supplier == supplier_field_utility_warehouse:
        answers[utility_warehouse_warning_page_field] = field_yes

    assert get_prev_page(own_property_page, answers) == expected_prev_page


def test_park_home_prev_page():
    assert get_prev_page(park_home_page, {}) == own_property_page


def test_park_home_main_residence_prev_page():
    assert get_prev_page(park_home_main_residence_page, {}) == park_home_page
