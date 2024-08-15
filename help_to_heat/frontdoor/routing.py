# page names
from help_to_heat.frontdoor.eligibility import calculate_eligibility

unknown_page = None
country_page = "country"
northern_ireland_ineligible_page = "northern-ireland"
supplier_page = "supplier"
own_property_page = "own-property"
bulb_warning_page = "bulb-warning-page"
utility_warehouse_warning_page = "utility-warehouse-warning-page"
park_home_page = "park-home"
park_home_main_residence_page = "park-home-main-residence"
park_home_ineligible_page = "park-home-application-closed"
address_page = "address"
epc_select_page = "epc-select"
address_select_page = "address-select"
referral_already_submitted_page = "referral-already-submitted"
address_manual_page = "address-manual"
council_tax_band_page = "council-tax-band"
epc_page = "epc"
epc_ineligible_page = "epc-ineligible"
benefits_page = "benefits"
household_income_page = "household-income-page"
property_ineligible_page = "ineligible"
property_type_page = "property-type"
property_subtype_page = "property-subtype"
number_of_bedrooms_page = "number-of-bedrooms"
wall_type_page = "wall-type"
wall_insulation_page = "wall-insulation"
loft_page = "loft"
loft_access_page = "loft-access"
loft_insulation_page = "loft-insulation"
summary_page = "summary"
schemes_page = "schemes"
contact_details_page = "contact-details"
confirm_and_submit_page = "confirm-and-submit"
success_page = "success"

# fields
field_yes = "Yes"
field_no = "No"
field_dont_know = "I do not know"
field_not_listed = "I do not see my option listed"

country_field = "country"
country_field_england = "England"
country_field_scotland = "Scotland"
country_field_wales = "Wales"
country_field_northern_ireland = "Northern Ireland"

supplier_field = "supplier"
supplier_field_british_gas = "British Gas"
supplier_field_bulb = "Bulb, now part of Octopus Energy"
supplier_field_e = "E (Gas & Electricity) Ltd"
supplier_field_edf = "EDF"
supplier_field_eon_next = "E.ON Next"
supplier_field_foxglove = "Foxglove"
supplier_field_octopus = "Octopus Energy"
supplier_field_ovo = "OVO"
supplier_field_scottish_power = "Scottish Power"
supplier_field_shell = "Shell"
supplier_field_utilita = "Utilita"
supplier_field_utility_warehouse = "Utility Warehouse"

bulb_warning_page_field = "confirm_bulb_warning"

utility_warehouse_warning_page_field = "confirm_utility_warehouse_warning"

own_property_field = "own_property"
own_property_field_own_property = "Yes, I own my property and live in it"
own_property_field_tenant = "No, I am a tenant"
own_property_field_social_housing = "No, I am a social housing tenant"
own_property_field_landlord = "Yes, I am the property owner but I lease the property to one or more tenants"
own_property_fields_non_social_housing = [own_property_field_own_property, own_property_field_tenant, own_property_field_landlord]

park_home_field = "park_home"
# yes/no options

park_home_main_residence_field = "park_home_main_residence"
# yes/no options

address_choice_field = "address_choice"
address_choice_field_write_address = "write address"
address_choice_field_enter_manually = "enter manually"
address_choice_duplicate_uprn_field = "address_select_uprn_is_duplicate"

epc_select_choice_field = "epc_select_choice"
epc_select_choice_field_select_epc = "select epc"
epc_select_choice_field_epc_api_fail = "epc api fail"
epc_select_choice_field_enter_manually = "enter manually"

address_select_choice_field = "address_select_choice"
address_select_choice_field_select_address = "select address"
address_select_choice_field_enter_manually = "enter manually"

duplicate_uprn_field = "uprn_is_duplicate"
epc_found_field = "epc_found"

council_tax_band_field = "council_tax_band"
council_tax_band_field_a = "A"
council_tax_band_field_b = "B"
council_tax_band_field_c = "C"
council_tax_band_field_d = "D"
council_tax_band_field_e = "E"
council_tax_band_field_f = "F"
council_tax_band_field_g = "G"
council_tax_band_field_h = "H"
council_tax_band_field_i = "I"

epc_accept_suggested_epc_field = "accept_suggested_epc"
epc_rating_is_eligible_field = "epc_rating_is_eligible"

benefits_field = "benefits"

household_income_field = "household_income"
household_income_field_less_than_threshold = "Less than £31,000 a year"
household_income_field_more_than_threshold = "£31,000 or more a year"

property_type_field = "property_type"
property_type_field_house = "House"
property_type_field_bungalow = "Bungalow"
property_type_field_apartment = "Apartment, flat or maisonette"
property_type_field_park_home = "Park home" # set if confirms yes to park home in flow

property_subtype_field = "property_subtype"
property_subtype_field_top_floor = "Top floor"
property_subtype_field_middle_floor = "Middle floor"
property_subtype_field_ground_floor = "Ground floor"
property_subtype_field_detached = "Detached"
property_subtype_field_semi_detached = "Semi-detached"
property_subtype_field_terraced = "Terraced"
property_subtype_field_end_terrace = "End terrace"

number_of_bedrooms_field = "number_of_bedrooms"
number_of_bedrooms_field_studio = "Studio"
number_of_bedrooms_field_one = "One bedroom"
number_of_bedrooms_field_two = "Two bedrooms"
number_of_bedrooms_field_three_or_more = "Three or more bedrooms"

wall_type_field = "wall_type"
wall_type_field_solid = "Solid walls"
wall_type_field_cavity = "Cavity walls"
wall_type_field_mix = "Mix of solid and cavity walls"
wall_type_field_not_listed = field_not_listed
wall_type_field_dont_know = field_dont_know

wall_insulation_field = "wall_insulation"
wall_insulation_field_yes = "Yes they are all insulated"
wall_insulation_field_some = "Some are insulated, some are not"
wall_insulation_field_no = "No they are not insulated"
wall_insulation_field_dont_know = field_dont_know

loft_field = "loft"
loft_field_yes = "Yes, I have a loft that has not been converted into a room"
loft_field_no = "No, I do not have a loft or my loft has been converted into a room"

loft_access_field = "loft_access"
loft_access_field_yes = "Yes, there is access to my loft"
loft_access_field_no = "No, there is no access to my loft"

loft_insulation_field = "loft_insulation"
loft_insulation_field_more_than_threshold = "I have more than 100mm of loft insulation"
loft_insulation_field_less_than_threshold = "I have up to 100mm of loft insulation"
loft_insulation_field_dont_know = field_dont_know


def requires_answer(answer_key):
    def wrapper(func):
        def next_page_function(answers):
            required_answer = answers.get(answer_key)
            if required_answer is None:
                return unknown_page

            return func(answers)
        return next_page_function
    return wrapper


def get_next_page(current_page, answers):
    if current_page == country_page:
        return _country_next_page(answers)

    if current_page == supplier_page:
        return _supplier_next_page(answers)

    if current_page == bulb_warning_page:
        return _bulb_warning_page_next_page(answers)

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

    if current_page == referral_already_submitted_page:
        return _referral_already_submitted_next_page(answers)

    if current_page == council_tax_band_page:
        return _council_tax_band_next_page(answers)

    if current_page == epc_page:
        return _epc_next_page(answers)

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
        return _summary_next_page(answers)

    if current_page == schemes_page:
        return _schemes_next_page(answers)

    if current_page == contact_details_page:
        return _contact_details_next_page(answers)

    if current_page == confirm_and_submit_page:
        return _confirm_and_submit_next_page(answers)

    return unknown_page


@requires_answer(country_field)
def _country_next_page(answers):
    country = answers.get(country_field)
    if country in [country_field_england, country_field_scotland, country_field_wales]:
        return supplier_page
    if country == country_field_northern_ireland:
        return northern_ireland_ineligible_page


@requires_answer(supplier_field)
def _supplier_next_page(answers):
    supplier = answers.get(supplier_field)
    if supplier in [supplier_field_british_gas, supplier_field_e, supplier_field_edf, supplier_field_eon_next,
                    supplier_field_foxglove, supplier_field_octopus, supplier_field_ovo, supplier_field_scottish_power,
                    supplier_field_shell, supplier_field_utilita]:
        return own_property_page
    if supplier == supplier_field_bulb:
        return bulb_warning_page
    if supplier == supplier_field_utility_warehouse:
        return utility_warehouse_warning_page


@requires_answer(bulb_warning_page_field)
def _bulb_warning_page_next_page(_answers):
    return own_property_page


@requires_answer(utility_warehouse_warning_page_field)
def _utility_warehouse_warning_page_next_page(_answers):
    return own_property_page


@requires_answer(own_property_field)
def _own_property_next_page(answers):
    own_property = answers.get(own_property_field)
    if own_property in own_property_fields_non_social_housing:
        return park_home_page
    if own_property == own_property_field_social_housing:
        return address_page

    return unknown_page


@requires_answer(park_home_field)
def _park_home_next_page(answers):
    park_home = answers.get(park_home_field)
    if park_home == field_yes:
        return park_home_main_residence_page
    if park_home == field_no:
        return address_page


@requires_answer(park_home_main_residence_field)
def _park_home_main_residence_next_page(answers):
    park_home_main_residence = answers.get(park_home_main_residence_field)
    if park_home_main_residence == field_no:
        return park_home_ineligible_page
    if park_home_main_residence == field_yes:
        return address_page


@requires_answer(address_choice_field)
def _address_next_page(answers):
    address_choice = answers.get(address_choice_field)
    country = answers.get(country_field)

    if address_choice == address_choice_field_write_address:
        if country in [country_field_england, country_field_wales]:
            return epc_select_page
        if country == country_field_scotland:
            return address_select_page
        return unknown_page
    if address_choice == address_choice_field_enter_manually:
        return address_manual_page


@requires_answer(epc_select_choice_field)
def _epc_select_next_page(answers):
    choice = answers.get(epc_select_choice_field)

    if choice == epc_select_choice_field_select_epc:
        return _post_address_input_next_page(answers)
    if choice == epc_select_choice_field_epc_api_fail:
        return address_select_page
    if choice == epc_select_choice_field_enter_manually:
        return address_manual_page


@requires_answer(address_select_choice_field)
def _address_select_next_page(answers):
    choice = answers.get(address_select_choice_field)

    if choice == address_select_choice_field_select_address:
        return _post_address_input_next_page(answers)
    if choice == address_choice_field_enter_manually:
        return address_manual_page


def _address_manual_next_page(answers):
    return _post_epc_next_page(answers)


# after submitting an address, show already submitted page or continue
def _post_address_input_next_page(answers):
    duplicate_uprn = answers.get(duplicate_uprn_field)
    if duplicate_uprn == field_yes:
        return referral_already_submitted_page
    if duplicate_uprn == field_no:
        return _post_duplicate_uprn_next_page(answers)
    return unknown_page


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


@requires_answer(council_tax_band_field)
def _council_tax_band_next_page(answers):
    return _post_council_tax_band_next_page(answers)


# confirms epc if it was found
def _post_council_tax_band_next_page(answers):
    epc_found = answers.get(epc_found_field)
    if epc_found == field_yes:
        return epc_page
    if epc_found == field_no:
        return _post_epc_next_page(answers)


@requires_answer(epc_accept_suggested_epc_field)
def _epc_next_page(answers):
    accept_suggested_epc = answers.get(epc_accept_suggested_epc_field)
    rating_is_eligible = answers.get(epc_rating_is_eligible_field)
    if accept_suggested_epc == field_yes and rating_is_eligible == field_no:
        return epc_ineligible_page
    else:
        return _post_epc_next_page(answers)


# ask circumstances questions, depending on flow
def _post_epc_next_page(answers):
    own_property = answers.get(own_property_field)
    if own_property in own_property_fields_non_social_housing:
        return benefits_page
    if own_property == own_property_field_social_housing:
        return _post_circumstances_next_page(answers)


@requires_answer(benefits_field)
def _benefits_next_page(answers):
    benefits = answers.get(benefits_field)
    if benefits == field_yes:
        return _post_circumstances_next_page(answers)
    if benefits == field_no:
        return household_income_page


@requires_answer(household_income_field)
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


@requires_answer(property_type_field)
def _property_type_next_page(_answers):
    return property_subtype_page


@requires_answer(property_subtype_field)
def _property_subtype_next_page(_answers):
    return number_of_bedrooms_page


@requires_answer(number_of_bedrooms_field)
def _number_of_bedrooms_next_page(_answers):
    return wall_type_page


@requires_answer(wall_type_field)
def _wall_type_next_page(_answers):
    return wall_insulation_page


@requires_answer(wall_insulation_field)
def _wall_insulation_next_page(_answers):
    return loft_page


@requires_answer(loft_field)
def _loft_next_page(answers):
    loft = answers.get(loft_field)

    if loft == loft_field_yes:
        return loft_access_page
    if loft == loft_field_no:
        return summary_page


@requires_answer(loft_access_field)
def _loft_access_next_page(_answers):
    return loft_insulation_page


@requires_answer(loft_insulation_field)
def _loft_insulation_next_page(_answers):
    return summary_page


def _summary_next_page(_answers):
    return schemes_page


def _schemes_next_page(_answers):
    return contact_details_page


def _contact_details_next_page(_answers):
    return confirm_and_submit_page


def _confirm_and_submit_next_page(_answers):
    return success_page
