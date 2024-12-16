from help_to_heat.frontdoor.consts import (
    address_choice_journey_field,
    address_choice_journey_field_enter_manually,
    address_choice_journey_field_epc_api_fail,
    address_choice_journey_field_write_address,
    address_manual_page,
    address_no_results_journey_field,
    address_page,
    address_select_choice_journey_field,
    address_select_choice_journey_field_select_address,
    address_select_manual_page,
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
    duplicate_uprn_journey_field,
    epc_accept_suggested_epc_field,
    epc_found_journey_field,
    epc_ineligible_page,
    epc_page,
    epc_rating_is_eligible_field,
    epc_select_choice_journey_field,
    epc_select_choice_journey_field_enter_manually,
    epc_select_choice_journey_field_epc_api_fail,
    epc_select_choice_journey_field_select_epc,
    epc_select_manual_page,
    epc_select_page,
    field_no,
    field_yes,
    govuk_start_page,
    household_income_field,
    household_income_page,
    loft_access_field,
    loft_access_page,
    loft_field,
    loft_field_no,
    loft_field_yes,
    loft_insulation_field,
    loft_insulation_page,
    loft_page,
    no_epc_field,
    no_epc_page,
    northern_ireland_ineligible_page,
    number_of_bedrooms_field,
    number_of_bedrooms_page,
    own_property_field,
    own_property_field_social_housing,
    own_property_fields_non_social_housing,
    own_property_page,
    park_home_field,
    park_home_ineligible_page,
    park_home_main_residence_field,
    park_home_main_residence_page,
    park_home_page,
    property_ineligible_page,
    property_subtype_field,
    property_subtype_page,
    property_type_field,
    property_type_page,
    referral_already_submitted_page,
    schemes_page,
    shell_warning_page,
    shell_warning_page_field,
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
    unknown_page,
    utility_warehouse_warning_page,
    utility_warehouse_warning_page_field,
    wall_insulation_field,
    wall_insulation_page,
    wall_type_field,
    wall_type_page,
)
from help_to_heat.frontdoor.eligibility import calculate_eligibility

_unknown_response = unknown_page


def _requires_answer(answer_key):
    def wrapper(func):
        def next_page_function(answers):
            required_answer = answers.get(answer_key)
            if required_answer is None:
                return _unknown_response

            return func(answers)

        return next_page_function

    return wrapper


def get_next_page(current_page, answers):
    """
    Generates the next page ID in the flow, given the users' current page and answers.
    Parameters
    ----------
    current_page
        Page ID the user is currently on.
    answers
        All answers given by the user so far. Should include answers submitted on the current page

    Returns
    -------
    str
        New page ID, or `unknown_page` (variable in consts.py) if the user hasn't given the required
        information on this page to determine the next page.
    """
    if current_page == govuk_start_page:
        return _govuk_start_page_next_page()

    if current_page == country_page:
        return _country_next_page(answers)

    if current_page == supplier_page:
        return _supplier_next_page(answers)

    if current_page == bulb_warning_page:
        return _bulb_warning_page_next_page(answers)

    if current_page == shell_warning_page:
        return _shell_warning_page_next_page(answers)

    if current_page == utility_warehouse_warning_page:
        return _utility_warehouse_warning_page_next_page(answers)

    if current_page == own_property_page:
        return _own_property_next_page(answers)

    if current_page == park_home_page:
        return _park_home_next_page(answers)

    if current_page == park_home_main_residence_page:
        return _park_home_main_residence_next_page(answers)

    if current_page == address_page:
        return _address_next_page(answers)

    if current_page == epc_select_page:
        return _epc_select_next_page(answers)

    if current_page == address_select_page:
        return _address_select_next_page(answers)

    if current_page == address_manual_page:
        return _address_manual_next_page(answers)

    if current_page == epc_select_manual_page:
        return _epc_select_manual_next_page(answers)

    if current_page == address_select_manual_page:
        return _address_select_manual_next_page(answers)

    if current_page == referral_already_submitted_page:
        return _referral_already_submitted_next_page(answers)

    if current_page == council_tax_band_page:
        return _council_tax_band_next_page(answers)

    if current_page == epc_page:
        return _epc_next_page(answers)

    if current_page == no_epc_page:
        return _no_epc_next_page(answers)

    if current_page == benefits_page:
        return _benefits_next_page(answers)

    if current_page == household_income_page:
        return _household_income_next_page(answers)

    if current_page == property_type_page:
        return _property_type_next_page(answers)

    if current_page == property_subtype_page:
        return _property_subtype_next_page(answers)

    if current_page == number_of_bedrooms_page:
        return _number_of_bedrooms_next_page(answers)

    if current_page == wall_type_page:
        return _wall_type_next_page(answers)

    if current_page == wall_insulation_page:
        return _wall_insulation_next_page(answers)

    if current_page == loft_page:
        return _loft_next_page(answers)

    if current_page == loft_access_page:
        return _loft_access_next_page(answers)

    if current_page == loft_insulation_page:
        return _loft_insulation_next_page(answers)

    if current_page == summary_page:
        return _summary_next_page()

    if current_page == schemes_page:
        return _schemes_next_page()

    if current_page == contact_details_page:
        return _contact_details_next_page()

    if current_page == confirm_and_submit_page:
        return _confirm_and_submit_next_page()

    return _unknown_response


def _govuk_start_page_next_page():
    return country_page


@_requires_answer(country_field)
def _country_next_page(answers):
    country = answers.get(country_field)
    if country in [country_field_england, country_field_scotland, country_field_wales]:
        return supplier_page
    if country == country_field_northern_ireland:
        return northern_ireland_ineligible_page
    return _unknown_response


@_requires_answer(supplier_field)
def _supplier_next_page(answers):
    supplier = answers.get(supplier_field)
    if supplier in [
        supplier_field_british_gas,
        supplier_field_e,
        supplier_field_edf,
        supplier_field_eon_next,
        supplier_field_foxglove,
        supplier_field_octopus,
        supplier_field_ovo,
        supplier_field_scottish_power,
        supplier_field_utilita,
    ]:
        return own_property_page
    if supplier == supplier_field_bulb:
        return bulb_warning_page
    if supplier == supplier_field_shell:
        return shell_warning_page
    if supplier == supplier_field_utility_warehouse:
        return utility_warehouse_warning_page
    return _unknown_response


# the answers object is not used by the function but is used by the decorator
@_requires_answer(bulb_warning_page_field)
def _bulb_warning_page_next_page(_answers):
    return own_property_page


@_requires_answer(shell_warning_page_field)
def _shell_warning_page_next_page(_answers):
    return own_property_page


@_requires_answer(utility_warehouse_warning_page_field)
def _utility_warehouse_warning_page_next_page(_answers):
    return own_property_page


@_requires_answer(own_property_field)
def _own_property_next_page(answers):
    own_property = answers.get(own_property_field)
    if own_property in own_property_fields_non_social_housing:
        return park_home_page
    if own_property == own_property_field_social_housing:
        return address_page

    return _unknown_response


@_requires_answer(park_home_field)
def _park_home_next_page(answers):
    park_home = answers.get(park_home_field)
    if park_home == field_yes:
        return park_home_main_residence_page
    if park_home == field_no:
        return address_page

    return _unknown_response


@_requires_answer(park_home_main_residence_field)
def _park_home_main_residence_next_page(answers):
    park_home_main_residence = answers.get(park_home_main_residence_field)
    if park_home_main_residence == field_no:
        return park_home_ineligible_page
    if park_home_main_residence == field_yes:
        return address_page

    return _unknown_response


@_requires_answer(address_choice_journey_field)
def _address_next_page(answers):
    address_choice = answers.get(address_choice_journey_field)
    address_no_results = answers.get(address_no_results_journey_field)
    country = answers.get(country_field)

    if address_no_results == field_yes:
        return address_manual_page
    if address_choice == address_choice_journey_field_write_address:
        if country in [country_field_england, country_field_wales]:
            return epc_select_page
        if country == country_field_scotland:
            return address_select_page
    if address_choice == address_choice_journey_field_epc_api_fail:
        return address_select_page
    if address_choice == address_choice_journey_field_enter_manually:
        return address_manual_page

    return _unknown_response


@_requires_answer(epc_select_choice_journey_field)
def _epc_select_next_page(answers):
    choice = answers.get(epc_select_choice_journey_field)

    if choice == epc_select_choice_journey_field_select_epc:
        return _post_address_input_next_page(answers)
    if choice == epc_select_choice_journey_field_epc_api_fail:
        return address_select_page
    if choice == epc_select_choice_journey_field_enter_manually:
        return epc_select_manual_page

    return _unknown_response


@_requires_answer(address_select_choice_journey_field)
def _address_select_next_page(answers):
    choice = answers.get(address_select_choice_journey_field)

    if choice == address_select_choice_journey_field_select_address:
        return _post_address_input_next_page(answers)
    if choice == address_choice_journey_field_enter_manually:
        return address_select_manual_page

    return _unknown_response


def _address_manual_next_page(answers):
    return _post_duplicate_uprn_next_page(answers)


def _epc_select_manual_next_page(answers):
    return _post_duplicate_uprn_next_page(answers)


def _address_select_manual_next_page(answers):
    return _post_duplicate_uprn_next_page(answers)


# after submitting an address, show already submitted page or continue
def _post_address_input_next_page(answers):
    duplicate_uprn = answers.get(duplicate_uprn_journey_field)
    if duplicate_uprn == field_yes:
        return referral_already_submitted_page
    if duplicate_uprn == field_no:
        return _post_duplicate_uprn_next_page(answers)

    return _unknown_response


def _referral_already_submitted_next_page(answers):
    return _post_duplicate_uprn_next_page(answers)


# show council tax band page or not, depending on flow
def _post_duplicate_uprn_next_page(answers):
    own_property = answers.get(own_property_field)
    park_home = answers.get(park_home_field)
    if own_property in own_property_fields_non_social_housing:
        if park_home == field_no:
            return council_tax_band_page
        if park_home == field_yes:
            return _post_council_tax_band_next_page(answers)
    if own_property == own_property_field_social_housing:
        return _post_council_tax_band_next_page(answers)

    return _unknown_response


@_requires_answer(council_tax_band_field)
def _council_tax_band_next_page(answers):
    return _post_council_tax_band_next_page(answers)


# confirms epc if it was found, or send to no epc
def _post_council_tax_band_next_page(answers):
    epc_found = answers.get(epc_found_journey_field)
    address_choice = answers.get(address_choice_journey_field)
    epc_select_choice = answers.get(epc_select_choice_journey_field)
    address_select_choice = answers.get(address_select_choice_journey_field)
    if epc_found == field_yes:
        return epc_page
    if epc_found == field_no:
        # if they entered an address manually, don't show the no epc page as an epc wasn't searched for
        # note that there are 3 address select pages so 3 places where the user can opt to enter manually
        if (
            address_choice == address_choice_journey_field_enter_manually
            or epc_select_choice == epc_select_choice_journey_field_enter_manually
            or address_select_choice == address_choice_journey_field_enter_manually
        ):
            return _post_epc_next_page(answers)

        return no_epc_page

    return _unknown_response


@_requires_answer(epc_accept_suggested_epc_field)
def _epc_next_page(answers):
    rating_is_eligible = answers.get(epc_rating_is_eligible_field)
    if rating_is_eligible == field_no:
        return epc_ineligible_page
    else:
        return _post_epc_next_page(answers)


@_requires_answer(no_epc_field)
def _no_epc_next_page(answers):
    return _post_epc_next_page(answers)


# ask circumstances questions, depending on flow
def _post_epc_next_page(answers):
    own_property = answers.get(own_property_field)
    if own_property in own_property_fields_non_social_housing:
        return benefits_page
    if own_property == own_property_field_social_housing:
        return _post_circumstances_next_page(answers)

    return _unknown_response


@_requires_answer(benefits_field)
def _benefits_next_page(answers):
    benefits = answers.get(benefits_field)
    if benefits == field_yes:
        return _post_circumstances_next_page(answers)
    if benefits == field_no:
        return household_income_page

    return _unknown_response


@_requires_answer(household_income_field)
def _household_income_next_page(answers):
    # re-use the existing eligibility logic
    # this code is trusted to be resilient against missing answers
    eligible_schemes = calculate_eligibility(answers)

    if len(eligible_schemes) == 0:
        return property_ineligible_page
    else:
        return _post_circumstances_next_page(answers)


# ask property questions, depending on flow
def _post_circumstances_next_page(answers):
    own_property = answers.get(own_property_field)
    park_home = answers.get(park_home_field)
    if own_property in own_property_fields_non_social_housing:
        if park_home == field_no:
            return property_type_page
        if park_home == field_yes:
            return summary_page
    if own_property == own_property_field_social_housing:
        return property_type_page

    return _unknown_response


@_requires_answer(property_type_field)
def _property_type_next_page(_answers):
    return property_subtype_page


@_requires_answer(property_subtype_field)
def _property_subtype_next_page(_answers):
    return number_of_bedrooms_page


@_requires_answer(number_of_bedrooms_field)
def _number_of_bedrooms_next_page(_answers):
    return wall_type_page


@_requires_answer(wall_type_field)
def _wall_type_next_page(_answers):
    return wall_insulation_page


@_requires_answer(wall_insulation_field)
def _wall_insulation_next_page(_answers):
    return loft_page


@_requires_answer(loft_field)
def _loft_next_page(answers):
    loft = answers.get(loft_field)

    if loft == loft_field_yes:
        return loft_access_page
    if loft == loft_field_no:
        return summary_page

    return _unknown_response


@_requires_answer(loft_access_field)
def _loft_access_next_page(_answers):
    return loft_insulation_page


@_requires_answer(loft_insulation_field)
def _loft_insulation_next_page(_answers):
    return summary_page


def _summary_next_page():
    return schemes_page


def _schemes_next_page():
    return contact_details_page


def _contact_details_next_page():
    return confirm_and_submit_page


def _confirm_and_submit_next_page():
    return success_page
