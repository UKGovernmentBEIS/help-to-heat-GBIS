from help_to_heat.frontdoor.consts import own_property_fields_non_social_housing, own_property_field, park_home_field, \
    field_yes, field_no, own_property_field_social_housing

flow_park_home = "park home flow"
flow_main = "main (not park) home flow"
flow_social_housing = "social housing flow"


def _get_park_home_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_yes}


def _get_main_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_no}


def _get_social_housing_flow_answers():
    yield {own_property_field: own_property_field_social_housing, park_home_field: field_no}


def _get_flow_answers(flow):
    if flow == flow_park_home:
        return list(_get_park_home_flow_answers())
    if flow == flow_main:
        return list(_get_main_flow_answers())
    if flow == flow_social_housing:
        return list(_get_social_housing_flow_answers())
