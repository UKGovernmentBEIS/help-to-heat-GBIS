from help_to_heat.frontdoor.consts import (
    bulb_warning_page_field,
    country_field,
    country_field_england,
    country_field_scotland,
    country_field_wales,
    field_no,
    field_yes,
    own_property_field,
    own_property_field_social_housing,
    own_property_fields_non_social_housing,
    park_home_field,
    supplier_field,
    supplier_field_bulb,
    supplier_field_utility_warehouse,
    supplier_fields,
    utility_warehouse_warning_page_field, park_home_main_residence_field, address_choice_field,
    address_choice_field_write_address, duplicate_uprn_field, epc_select_choice_field,
    epc_select_choice_field_select_epc, epc_found_field, epc_select_choice_field_epc_api_fail,
    address_select_choice_field, address_select_choice_field_select_address, address_select_choice_field_enter_manually,
    epc_select_choice_field_enter_manually, address_choice_field_enter_manually,
)

flow_park_home = "park home flow"
flow_main = "main (not park) home flow"
flow_social_housing = "social housing flow"
all_flows = [flow_park_home, flow_main, flow_social_housing]


def get_country_answers():
    yield {country_field: country_field_england}
    yield {country_field: country_field_scotland}
    yield {country_field: country_field_wales}


def get_supplier_answers():
    for country_answers in get_country_answers():
        for supplier in supplier_fields:
            answers = {**country_answers, supplier_field: supplier}

            if supplier == supplier_field_bulb:
                answers[bulb_warning_page_field] = field_yes
            if supplier == supplier_field_utility_warehouse:
                answers[utility_warehouse_warning_page_field] = field_yes

            yield answers


def _get_park_home_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {
            own_property_field: own_property,
            park_home_field: field_yes,
            park_home_main_residence_field: field_yes
        }


def _get_main_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_no}


def _get_social_housing_flow_answers():
    yield {own_property_field: own_property_field_social_housing, park_home_field: field_no}


def get_flow_answers(flow):
    for supplier_answers in get_supplier_answers():
        all_flow_answers = []
        if flow == flow_park_home:
            all_flow_answers = _get_park_home_flow_answers()
        if flow == flow_main:
            all_flow_answers = _get_main_flow_answers()
        if flow == flow_social_housing:
            all_flow_answers = _get_social_housing_flow_answers()

        for flow_answers in all_flow_answers:
            yield {**supplier_answers, **flow_answers}


def get_all_flow_answers():
    for flow in all_flows:
        for flow_answers in get_flow_answers(flow):
            yield flow_answers


def _get_address_input_answers_pre_duplicate_uprn():
    for flow_answers in get_all_flow_answers():
        country = flow_answers[country_field]

        if country in [country_field_england, country_field_wales]:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_select_epc,
                epc_found_field: field_yes
            }

            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no
            }

            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

        if country == country_field_scotland:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_yes
            }

            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no
            }

            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

        yield {
            **flow_answers,
            address_choice_field: address_choice_field_enter_manually,
            epc_found_field: field_no
        }


def get_address_input_answers():
    for address_answers in _get_address_input_answers_pre_duplicate_uprn():
        yield {
            **address_answers,
            duplicate_uprn_field: field_yes
        }
        yield {
            **address_answers,
            duplicate_uprn_field: field_no
        }
