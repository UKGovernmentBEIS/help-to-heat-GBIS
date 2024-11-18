from help_to_heat.frontdoor.consts import (
    address_choice_field,
    address_choice_field_enter_manually,
    address_choice_field_epc_api_fail,
    address_choice_field_write_address,
    address_select_choice_field,
    address_select_choice_field_enter_manually,
    address_select_choice_field_select_address,
    benefits_field,
    bulb_warning_page_field,
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
    council_tax_band_fields,
    country_field,
    country_field_england,
    country_field_scotland,
    country_field_wales,
    duplicate_uprn_field,
    epc_accept_suggested_epc_field,
    epc_found_field,
    epc_rating_is_eligible_field,
    epc_select_choice_field,
    epc_select_choice_field_enter_manually,
    epc_select_choice_field_epc_api_fail,
    epc_select_choice_field_select_epc,
    field_dont_know,
    field_no,
    field_yes,
    household_income_field,
    household_income_field_less_than_threshold,
    loft_access_field,
    loft_access_field_no,
    loft_access_field_yes,
    loft_field,
    loft_field_no,
    loft_field_yes,
    loft_insulation_field,
    loft_insulation_field_dont_know,
    loft_insulation_field_less_than_threshold,
    loft_insulation_field_more_than_threshold,
    loft_insulation_field_no_insulation,
    no_epc_field,
    number_of_bedrooms_field,
    number_of_bedrooms_field_one,
    number_of_bedrooms_field_studio,
    number_of_bedrooms_field_three_or_more,
    number_of_bedrooms_field_two,
    own_property_field,
    own_property_field_social_housing,
    own_property_fields_non_social_housing,
    park_home_field,
    park_home_main_residence_field,
    property_subtype_field,
    property_subtype_field_detached,
    property_subtype_field_end_terrace,
    property_subtype_field_ground_floor,
    property_subtype_field_middle_floor,
    property_subtype_field_semi_detached,
    property_subtype_field_terraced,
    property_subtype_field_top_floor,
    property_type_field,
    property_type_field_apartment,
    property_type_field_bungalow,
    property_type_field_house,
    shell_warning_page_field,
    supplier_field,
    supplier_field_bulb,
    supplier_field_shell,
    supplier_field_utility_warehouse,
    supplier_fields,
    utility_warehouse_warning_page_field,
    wall_insulation_field,
    wall_insulation_field_dont_know,
    wall_insulation_field_no,
    wall_insulation_field_some,
    wall_insulation_field_yes,
    wall_type_field,
    wall_type_field_cavity,
    wall_type_field_dont_know,
    wall_type_field_mix,
    wall_type_field_not_listed,
    wall_type_field_solid,
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
    address_flow_manually,
]

circumstances_flow_benefits_eligible = "benefits"
circumstances_flow_income_eligible = "income"
all_circumstances_flows = [
    circumstances_flow_benefits_eligible,
    circumstances_flow_income_eligible,
]

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

loft_flow_yes = "loft yes"
loft_flow_no = "loft no"
all_loft_flows = [loft_flow_yes, loft_flow_no]


# when testing the routing functions, we need some functions to generate answer objects.
# however, it is not enough to generate answer objects that contain only one or two answers.
# since the back routing reconstructs the entire route, it is necessary to have all previous answers given.

# so, a series of generators are given.
# these will generate a sequence of answer objects.
# this sequence will contain all permutations of answer objects that can exist at this stage in the questionnaire.
# ie all possible routes through entering an address. invalid answer objects should not be generated.
# this is done by having the generators chained together.
# ie get_supplier_answers iterates through all answer objects generated by get_country_answers.
# for each of these answer objects, yield answer objects for every supplier
# this generates a lot of answer objects over time but the function being tested is quick so this is fine

# when making changes to the routing or questions, make sure these generators remain accurate.
# if there are fails in test_backwards_routing, it is most likely that the generators aren't generating valid answer
# objects that can reconstruct the route.

# since in the later stages of the form there is such a large amount of possible answer objects, some trimming is done.
# the answers to the house question don't really matter to the flow then we pick one valid answer object for the
# prior questions and generate based on that


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
            if supplier == supplier_field_shell:
                answers[shell_warning_page_field] = field_yes
            if supplier == supplier_field_utility_warehouse:
                answers[utility_warehouse_warning_page_field] = field_yes

            yield answers


def _get_park_home_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_yes, park_home_main_residence_field: field_yes}


def _get_main_flow_answers():
    for own_property in own_property_fields_non_social_housing:
        yield {own_property_field: own_property, park_home_field: field_no}


def _get_social_housing_flow_answers():
    yield {own_property_field: own_property_field_social_housing, park_home_field: field_no}


def get_property_flow_answers(property_flow=None):
    if property_flow is not None:
        property_flows = [property_flow]
    else:
        property_flows = all_property_flows

    for check_property_flow in property_flows:
        for supplier_answers in get_supplier_answers():
            all_flow_answers = []
            if check_property_flow == property_flow_park_home:
                all_flow_answers = _get_park_home_flow_answers()
            if check_property_flow == property_flow_main:
                all_flow_answers = _get_main_flow_answers()
            if check_property_flow == property_flow_social_housing:
                all_flow_answers = _get_social_housing_flow_answers()

            for flow_answers in all_flow_answers:
                yield {**supplier_answers, **flow_answers}


def _get_address_input_answers_pre_duplicate_uprn(address_flow, property_flow=None):
    for flow_answers in get_property_flow_answers(property_flow):
        country = flow_answers.get(country_field)
        # if country wouldn't allow this flow then skip
        if (
            address_flow
            in [
                address_flow_write_address_epc_hit_select,
                address_flow_write_address_epc_hit_write_manually,
                address_flow_write_address_epc_api_fail_select,
                address_flow_write_address_epc_api_fail_manually,
            ]
            and country == country_field_scotland
        ):
            continue
        if address_flow in [
            address_flow_write_address_scotland_select_epc,
            address_flow_write_address_scotland_select_no_epc,
            address_flow_write_address_scotland_manually,
        ] and country in [country_field_england, country_field_wales]:
            continue

        if address_flow == address_flow_write_address_epc_hit_select:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_select_epc,
                epc_found_field: field_yes,
            }

        if address_flow == address_flow_write_address_epc_hit_write_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_enter_manually,
                epc_found_field: field_no,
            }

        if address_flow == address_flow_write_address_epc_api_fail_select:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no,
            }
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no,
            }

        if address_flow == address_flow_write_address_epc_api_fail_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no,
            }
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                epc_select_choice_field: epc_select_choice_field_epc_api_fail,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no,
            }

        if address_flow == address_flow_write_address_scotland_select_epc:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_yes,
            }

        if address_flow == address_flow_write_address_scotland_select_no_epc:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_select_address,
                epc_found_field: field_no,
            }

        if address_flow == address_flow_write_address_scotland_manually:
            yield {
                **flow_answers,
                address_choice_field: address_choice_field_write_address,
                address_select_choice_field: address_select_choice_field_enter_manually,
                epc_found_field: field_no,
            }

        if address_flow == address_flow_manually:
            yield {**flow_answers, address_choice_field: address_choice_field_enter_manually, epc_found_field: field_no}


# answers for after the user has entered an address either by select or manually
def get_address_answers(address_flow, duplicate_uprn=None, property_flow=None):
    for address_answers in _get_address_input_answers_pre_duplicate_uprn(address_flow, property_flow):
        if duplicate_uprn is not None:
            yield {**address_answers, duplicate_uprn_field: duplicate_uprn}
        else:
            # if flow is one where a UPRN is checked, add options for whether a UPRN hit happened
            if address_flow in [
                address_flow_write_address_epc_hit_select,
                address_flow_write_address_epc_api_fail_select,
                address_flow_write_address_scotland_select_epc,
                address_flow_write_address_scotland_select_no_epc,
            ]:
                yield {**address_answers, duplicate_uprn_field: field_yes}
                yield {**address_answers, duplicate_uprn_field: field_no}
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
                    yield {**address_answers, council_tax_band_field: council_tax_band}
            else:
                yield address_answers


def get_epc_answers(address_flow=None, duplicate_uprn=None, property_flow=None):
    if address_flow is not None:
        address_flows = [address_flow]
    else:
        address_flows = all_address_flows

    for check_address_flow in address_flows:
        for council_tax_band_answers in get_council_tax_band_answers(check_address_flow, duplicate_uprn, property_flow):
            if check_address_flow in [
                address_flow_write_address_epc_hit_select,
                address_flow_write_address_scotland_select_epc,
            ]:
                # if they would hit the epc page
                yield {
                    **council_tax_band_answers,
                    epc_accept_suggested_epc_field: field_no,
                    epc_rating_is_eligible_field: field_yes,
                }
                yield {
                    **council_tax_band_answers,
                    epc_accept_suggested_epc_field: field_dont_know,
                    epc_rating_is_eligible_field: field_yes,
                }
                yield {
                    **council_tax_band_answers,
                    epc_accept_suggested_epc_field: field_yes,
                    epc_rating_is_eligible_field: field_yes,
                }
            else:
                # else they would hit the no-epc page
                yield {**council_tax_band_answers, no_epc_field: field_yes}


def get_circumstances_answers(circumstances_flow=None, address_flow=None, duplicate_uprn=None, property_flow=None):
    if circumstances_flow is not None:
        circumstances_flows = [circumstances_flow]
    else:
        circumstances_flows = all_circumstances_flows

    if property_flow is not None:
        property_flows = [property_flow]
    else:
        property_flows = all_property_flows

    for check_circumstances_flow in circumstances_flows:
        for check_property_flow in property_flows:
            for epc_answers in get_epc_answers(address_flow, duplicate_uprn, check_property_flow):
                # only append these answers if on not social housing flow
                if check_property_flow in [property_flow_park_home, property_flow_main]:
                    if check_circumstances_flow == circumstances_flow_benefits_eligible:
                        yield {**epc_answers, benefits_field: field_yes}

                    if check_circumstances_flow == circumstances_flow_income_eligible:
                        yield {
                            **epc_answers,
                            benefits_field: field_no,
                            household_income_field: household_income_field_less_than_threshold,
                        }
                else:
                    yield epc_answers


def get_property_type_answers():
    # property type questions not asked on park home flow
    for circumstances_answers in [
        next(get_circumstances_answers(property_flow=property_flow_main)),
        next(get_circumstances_answers(property_flow=property_flow_social_housing)),
    ]:
        for property_subtype in [
            property_subtype_field_detached,
            property_subtype_field_semi_detached,
            property_subtype_field_terraced,
            property_subtype_field_end_terrace,
        ]:
            yield {
                **circumstances_answers,
                property_type_field: property_type_field_house,
                property_subtype_field: property_subtype,
            }

        for property_subtype in [
            property_subtype_field_detached,
            property_subtype_field_semi_detached,
            property_subtype_field_terraced,
            property_subtype_field_end_terrace,
        ]:
            yield {
                **circumstances_answers,
                property_type_field: property_type_field_bungalow,
                property_subtype_field: property_subtype,
            }

        for property_subtype in [
            property_subtype_field_top_floor,
            property_subtype_field_middle_floor,
            property_subtype_field_ground_floor,
            property_subtype_field_end_terrace,
        ]:
            yield {
                **circumstances_answers,
                property_type_field: property_type_field_apartment,
                property_subtype_field: property_subtype,
            }


def get_number_of_bedrooms_answers():
    answers = next(get_property_type_answers())
    yield {**answers, number_of_bedrooms_field: number_of_bedrooms_field_studio}
    yield {**answers, number_of_bedrooms_field: number_of_bedrooms_field_one}
    yield {**answers, number_of_bedrooms_field: number_of_bedrooms_field_two}
    yield {**answers, number_of_bedrooms_field: number_of_bedrooms_field_three_or_more}


def get_wall_type_answers():
    answers = next(get_number_of_bedrooms_answers())
    yield {**answers, wall_type_field: wall_type_field_solid}
    yield {**answers, wall_type_field: wall_type_field_cavity}
    yield {**answers, wall_type_field: wall_type_field_mix}
    yield {**answers, wall_type_field: wall_type_field_not_listed}
    yield {**answers, wall_type_field: wall_type_field_dont_know}


def get_wall_insulation_answers():
    answers = next(get_wall_type_answers())
    yield {**answers, wall_insulation_field: wall_insulation_field_yes}
    yield {**answers, wall_insulation_field: wall_insulation_field_some}
    yield {**answers, wall_insulation_field: wall_insulation_field_no}
    yield {**answers, wall_insulation_field: wall_insulation_field_dont_know}


def get_loft_answers(loft_flow=None):
    if loft_flow is not None:
        loft_flows = [loft_flow]
    else:
        loft_flows = all_loft_flows

    for check_loft_flow in loft_flows:
        answers = next(get_wall_insulation_answers())
        if check_loft_flow == loft_flow_yes:
            yield {**answers, loft_field: loft_field_yes}
        if check_loft_flow == loft_flow_no:
            yield {**answers, loft_field: loft_field_no}


def get_loft_access_answers():
    answers = next(get_loft_answers(loft_flow_yes))
    yield {**answers, loft_access_field: loft_access_field_yes}
    yield {**answers, loft_access_field: loft_access_field_no}


def get_loft_insulation_answers():
    answers = next(get_loft_access_answers())
    yield {**answers, loft_insulation_field: loft_insulation_field_more_than_threshold}
    yield {**answers, loft_insulation_field: loft_insulation_field_less_than_threshold}
    yield {**answers, loft_insulation_field: loft_insulation_field_no_insulation}
    yield {**answers, loft_insulation_field: loft_insulation_field_dont_know}


def get_summary_answers():
    for answers in get_loft_insulation_answers():
        yield answers

    for answers in get_loft_answers(loft_flow_no):
        yield answers

    for answers in get_circumstances_answers(property_flow=property_flow_park_home):
        yield answers
