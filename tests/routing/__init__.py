from help_to_heat.frontdoor.consts import *

flow_park_home = "park home flow"
flow_main = "main (not park) home flow"
flow_social_housing = "social housing flow"


def _get_country_answers():
    yield {country_field: country_field_england}
    yield {country_field: country_field_scotland}
    yield {country_field: country_field_wales}


def _get_supplier_answers():
    for country_answers in _get_country_answers():
        for supplier in supplier_fields:
            answers = {
                **country_answers,
                supplier_field: supplier
            }

            if supplier == supplier_field_bulb:
                answers[bulb_warning_page_field] = field_yes
            if supplier == supplier_field_utility_warehouse:
                answers[utility_warehouse_warning_page_field] = field_yes

            yield answers


def _get_park_home_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_yes}


def _get_main_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_no}


def _get_social_housing_flow_answers():
    yield {own_property_field: own_property_field_social_housing, park_home_field: field_no}


def _get_flow_answers(flow):
    for supplier_answers in _get_supplier_answers():
        all_flow_answers = []
        if flow == flow_park_home:
            all_flow_answers = _get_park_home_flow_answers()
        if flow == flow_main:
            all_flow_answers = _get_main_flow_answers()
        if flow == flow_social_housing:
            all_flow_answers = _get_social_housing_flow_answers()

        for flow_answers in all_flow_answers:
            yield {
                **supplier_answers,
                **flow_answers
            }
