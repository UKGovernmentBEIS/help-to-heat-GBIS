# page name
unknown_page = "UNKNOWN-PAGE"
govuk_start_page = "start_page"
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
supplier_fields = [
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

bulb_warning_page_field = "confirm_bulb_warning"

utility_warehouse_warning_page_field = "confirm_utility_warehouse_warning"

own_property_field = "own_property"
own_property_field_own_property = "Yes, I own my property and live in it"
own_property_field_tenant = "No, I am a tenant"
own_property_field_social_housing = "No, I am a social housing tenant"
own_property_field_landlord = "Yes, I am the property owner but I lease the property to one or more tenants"
own_property_fields_non_social_housing = [
    own_property_field_own_property,
    own_property_field_tenant,
    own_property_field_landlord,
]

park_home_field = "park_home"
# yes/no options

park_home_main_residence_field = "park_home_main_residence"
# yes/no options

address_choice_field = "address_choice"
address_choice_field_write_address = "write address"
address_choice_field_enter_manually = "enter manually"

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
council_tax_field_bands = [
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
epc_rating_is_eligible_field = "epc_rating_is_eligible"

benefits_field = "benefits"

household_income_field = "household_income"
household_income_field_less_than_threshold = "Less than £31,000 a year"
household_income_field_more_than_threshold = "£31,000 or more a year"

property_type_field = "property_type"
property_type_field_house = "House"
property_type_field_bungalow = "Bungalow"
property_type_field_apartment = "Apartment, flat or maisonette"
property_type_field_park_home = "Park home"  # set if confirms yes to park home in flow

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
