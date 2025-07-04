# page name
# a couple of the page strings contain a -page suffix in the value (eg "bulb-warning-page").
# we have moved away from doing this (it's redundant), but the -page must be left there.
# this is because changing a page name is breaking, it is used for the urls,
# as well as associating questions with pages in the database.
unknown_page = "UNKNOWN-PAGE"
govuk_start_page = "start_page"
country_page = "country"
northern_ireland_ineligible_page = "northern-ireland"
supplier_page = "supplier"
alternative_supplier_page = "alternative-supplier"
own_property_page = "own-property"
bulb_warning_page = "bulb-warning-page"
shell_warning_page = "shell-warning-page"
utility_warehouse_warning_page = "utility-warehouse-warning-page"
property_type_page = "property-type"
property_subtype_page = "property-subtype"
cannot_continue_page = "cannot-continue"
address_page = "address"
epc_select_page = "epc-select"
address_select_page = "address-select"
referral_already_submitted_page = "referral-already-submitted"
address_manual_page = "address-manual"
epc_select_manual_page = "epc-select-manual"
address_select_manual_page = "address-select-manual"
council_tax_band_page = "council-tax-band"
epc_page = "epc"
no_epc_page = "no-epc"
epc_ineligible_page = "epc-ineligible"
benefits_page = "benefits"
household_income_page = "household-income"
property_ineligible_page = "ineligible"
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
all_pages = [
    govuk_start_page,
    country_page,
    northern_ireland_ineligible_page,
    supplier_page,
    alternative_supplier_page,
    own_property_page,
    bulb_warning_page,
    shell_warning_page,
    utility_warehouse_warning_page,
    property_type_page,
    property_subtype_page,
    cannot_continue_page,
    address_page,
    epc_select_page,
    address_select_page,
    referral_already_submitted_page,
    address_manual_page,
    epc_select_manual_page,
    address_select_manual_page,
    council_tax_band_page,
    epc_page,
    no_epc_page,
    epc_ineligible_page,
    benefits_page,
    household_income_page,
    property_ineligible_page,
    number_of_bedrooms_page,
    wall_type_page,
    wall_insulation_page,
    loft_page,
    loft_access_page,
    loft_insulation_page,
    summary_page,
    schemes_page,
    contact_details_page,
    confirm_and_submit_page,
    success_page,
]

# fields and field options
field_yes = "Yes"
field_no = "No"
field_dont_know = "I do not know"
field_not_listed = "I do not see my option listed"

country_field = "country"
country_field_england = "England"
country_field_scotland = "Scotland"
country_field_wales = "Wales"
country_field_northern_ireland = "Northern Ireland"

# if needing to query this, in most cases use SupplierConverter.get_supplier()
# it handles the user selecting an alternative
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
supplier_field_values_real = [
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
]
supplier_field_not_listed = "supplier_not_listed"

alternative_supplier_field = "alternative_supplier"

user_selected_supplier_field = "user_selected_supplier"

bulb_warning_page_field = "confirm_bulb_warning"

shell_warning_page_field = "confirm_shell_warning"

utility_warehouse_warning_page_field = "confirm_utility_warehouse_warning"

own_property_field = "own_property"
own_property_field_own_property = "Yes, I own my property and live in it"
own_property_field_tenant = "No, I am a tenant"
own_property_field_social_housing = "No, I am a social housing tenant"
own_property_field_landlord = "Yes, I am the property owner but I lease the property to one or more tenants"
own_property_field_values_can_continue = [
    own_property_field_own_property,
    own_property_field_tenant,
    own_property_field_landlord,
]

property_type_field = "property_type"
property_type_field_house = "House"
property_type_field_bungalow = "Bungalow"
property_type_field_apartment = "Apartment, flat or maisonette"
property_type_field_park_home = "Park home"

property_subtype_field = "property_subtype"
property_subtype_field_top_floor = "Top floor"  # deprecated, tied to apartment property type which is now ineligible
property_subtype_field_middle_floor = (
    "Middle floor"  # deprecated, tied to apartment property type which is now ineligible
)
property_subtype_field_ground_floor = (
    "Ground floor"  # deprecated, tied to apartment property type which is now ineligible
)
property_subtype_field_detached = "Detached"
property_subtype_field_semi_detached = "Semi-detached"
property_subtype_field_terraced = "Terraced"
property_subtype_field_end_terrace = "End terrace"

# deprecated, this question was merged into property_type_field
park_home_field = "park_home"
# yes/no options

# deprecated, this question is no longer asked
park_home_main_residence_field = "park_home_main_residence"
# yes/no options

address_building_name_or_number_field = "building_name_or_number"
address_postcode_field = "postcode"
# this const was renamed to no longer include lmk.
# this is as this field stores info from both flows (lmk & uprn)
# the field value is left as is to preserve backwards compatibility
address_all_address_and_details_field = "address_and_lmk_details"

# journey fields are calculated based on user input & other factors, and decide where the user should go next
# they are stored in the users' session to record the result of these checks, to make journey calculation reproducible
address_choice_journey_field = "address_choice"
address_choice_journey_field_write_address = "write address"
address_choice_journey_field_epc_api_fail = "epc api fail"
address_choice_journey_field_enter_manually = "enter manually"
address_no_results_journey_field = "no_results"  # yes/no options

epc_select_choice_journey_field = "epc_select_choice"
epc_select_choice_journey_field_select_epc = "select epc"
epc_select_choice_journey_field_epc_api_fail = "epc api fail"
epc_select_choice_journey_field_enter_manually = "enter manually"

address_select_choice_journey_field = "address_select_choice"
address_select_choice_journey_field_select_address = "select address"
address_select_choice_journey_field_enter_manually = "enter manually"

# note that this field was not originally saved to the session correctly, so not all journeys have this set
# this was since it originally was not a field used for routing.
# because of this, we can't depend on this field for making routing decisions
referral_already_submitted_journey_field = "submit_another"

# likewise, this field was only added when it was required to block submissions to the same supplier
# if unset, we cannot know if the user has submitted to the same supplier or not
referral_submitted_to_same_supplier_journey_field = "submitted_to_same_supplier"  # yes/no options

address_manual_address_line_1_field = "address_line_1"
address_manual_address_line_2_field = "address_line_2"
address_manual_town_or_city_field = "town_or_city"
address_manual_county_field = "county"
address_manual_postcode_field = "postcode"

duplicate_uprn_journey_field = "uprn_is_duplicate"  # yes/no options
epc_found_journey_field = "epc_found"  # yes/no options
lmk_field = "lmk"
lmk_field_enter_manually = "enter-manually"
address_field = "address"
epc_details_field = "epc_details"
recommendations_field = "recommendations"
uprn_field = "uprn"
uprn_field_enter_manually = "enter-manually"
property_main_heat_source_field = "property_main_heat_source"  # deprecated, superseded by info in epc_details

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
council_tax_band_field_values = [
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
    council_tax_band_field_i,
]

epc_accept_suggested_epc_field = "accept_suggested_epc"
epc_accept_suggested_epc_field_not_found = "Not found"
epc_rating_field = "epc_rating"
epc_rating_field_not_found = "Not found"
epc_rating_is_eligible_field = "epc_rating_is_eligible"  # yes/no options

no_epc_field = "confirm_no_epc"  # yes/no options

benefits_field = "benefits"

household_income_field = "household_income"
household_income_field_less_than_threshold = "Less than £31,000 a year"
household_income_field_more_than_threshold = "£31,000 or more a year"

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
loft_access_field_no_loft = "No loft"

loft_insulation_field = "loft_insulation"
loft_insulation_field_more_than_threshold = "I have more than 100mm of loft insulation"
loft_insulation_field_less_than_threshold = "I have less than or equal to 100mm of loft insulation"
loft_insulation_field_no_insulation = "I have no loft insulation"
loft_insulation_field_dont_know = field_dont_know
loft_insulation_field_no_loft = "No loft"

schemes_ventilation_acknowledgement_field = "ventilation_acknowledgement"
schemes_contribution_acknowledgement_field = "contribution_acknowledgement"


contact_details_first_name_field = "first_name"
contact_details_last_name_field = "last_name"
contact_details_contact_number_field = "contact_number"
contact_details_email_field = "email"

confirm_and_submit_permission_field = "permission"
confirm_and_submit_acknowledge_field = "acknowledge"

page_name_field = "_page_name"
schemes_field = "schemes"

# other
# also is used in frontdoor/base.html
govuk_start_page_url = "https://www.gov.uk/apply-great-british-insulation-scheme"
