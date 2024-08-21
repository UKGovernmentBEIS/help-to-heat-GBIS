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
    epc_select_choice_field_enter_manually, address_choice_field_enter_manually, council_tax_band_fields,
    council_tax_band_field, epc_accept_suggested_epc_field, field_dont_know,
)

property_flow_park_home = "park home flow"
property_flow_main = "main (not park) home flow"
property_flow_social_housing = "social housing flow"
all_property_flows = [property_flow_park_home, property_flow_main, property_flow_social_housing]

address_flow_write_address_epc_hit_select = "epc hit select"
address_flow_write_address_epc_hit_write_manually = "epc hit manually"
address_flow_write_address_epc_api_fail_select = "epc fail select"
address_flow_write_address_epc_api_fail_manually = "epc fail manually"
address_flow_write_address_scotland_select_epc = "scotland select epc found"
address_flow_write_address_scotland_select_no_epc = "scotland select epc not found"
address_flow_write_address_scotland_manually = "scotland manually"
address_flow_manually = "manually"
all_address_flows = [
    address_flow_write_address_epc_hit_select,
    address_flow_write_address_epc_hit_write_manually,
    address_flow_write_address_epc_api_fail_select,
    address_flow_write_address_epc_api_fail_manually,
    address_flow_write_address_scotland_select_epc,
    address_flow_write_address_scotland_select_no_epc,
    address_flow_write_address_scotland_manually,
    address_flow_manually
]


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


def get_property_flow_answers(flow):
    for supplier_answers in get_supplier_answers():
        all_flow_answers = []
        if flow == property_flow_park_home:
            all_flow_answers = _get_park_home_flow_answers()
        if flow == property_flow_main:
            all_flow_answers = _get_main_flow_answers()
        if flow == property_flow_social_housing:
            all_flow_answers = _get_social_housing_flow_answers()

        for flow_answers in all_flow_answers:
            yield {**supplier_answers, **flow_answers}


def get_all_property_flow_answers():
    for flow in all_property_flows:
        for flow_answers in get_property_flow_answers(flow):
            yield flow_answers


def _get_address_input_answers_pre_duplicate_uprn(address_flow, property_flow=None):
    if property_flow is not None:
        property_flow_answers = get_property_flow_answers(property_flow)
    else:
        property_flow_answers = get_all_property_flow_answers()

    for flow_answers in property_flow_answers:
        if address_flow == address_flow_write_address_epc_hit_select:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_select_epc,
                epc_found_field: field_yes
            }

        if address_flow == address_flow_write_address_epc_hit_write_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

        if address_flow == address_flow_write_address_epc_api_fail_select:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no
            }

        if address_flow == address_flow_write_address_epc_api_fail_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

        if address_flow == address_flow_write_address_scotland_select_epc:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_yes
            }

        if address_flow == address_flow_write_address_scotland_select_no_epc:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no
            }

        if address_flow == address_flow_write_address_scotland_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no
            }

        if address_flow == address_flow_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_enter_manually,
                epc_found_field: field_no
            }


# answers for after the user has entered an address either by select or manually
def get_address_answers(address_flow, duplicate_uprn=None, property_flow=None):
    for address_answers in _get_address_input_answers_pre_duplicate_uprn(address_flow, property_flow):
        if duplicate_uprn is not None:
            yield {
                **address_answers,
                duplicate_uprn_field: duplicate_uprn
            }
        else:
            # if flow is one where a UPRN is checked, add options for whether a UPRN hit happened
            if address_flow in [address_flow_write_address_epc_hit_select, address_flow_write_address_epc_api_fail_select, address_flow_write_address_scotland_select]:
                yield {
                    **address_answers,
                    duplicate_uprn_field: field_yes
                }
                yield {
                    **address_answers,
                    duplicate_uprn_field: field_no
                }
            else:
                yield address_answers


# adds on the options for council tax bands, if necessary
def get_council_tax_band_answers(address_flow, duplicate_uprn=None, property_flow=None):
    if property_flow is not None:
        property_flows = [property_flow]
    else:
        property_flows = all_property_flows

    for check_property_flow in property_flows:
        for address_answers in get_address_answers(address_flow, duplicate_uprn, check_property_flow):
            if check_property_flow == property_flow_main:
                for council_tax_band in council_tax_band_fields:
                    yield {
                        **address_answers,
                        council_tax_band_field: council_tax_band
                    }
            else:
                yield address_answers


# def get_epc_answers(address_flow, duplicate_uprn=None, property_flow=None):
#     if address_flow is not None:
#         address_flows = [address_flow]
#     else:
#         address_flows = all_address_flows
#
#     for check_address_flow in address_flows:
#         for council_tax_band_answers in get_council_tax_band_answers(address_flow, duplicate_uprn, property_flow):
#             if check_address_flow in [address_flow_write_address_epc_hit_select, address_flow_write_address_scotland_select_epc]:
#                 yield {
#                     **council_tax_band_answers,
#                     epc_accept_suggested_epc_field: field_no
#                 }
#                 yield {
#                     **council_tax_band_answers,
#                     epc_accept_suggested_epc_field: field_dont_know
#                 }
#                 yield {
#                     **council_tax_band_answers,
#                     epc_accept_suggested_epc_field: field_dont_know
#                 }
