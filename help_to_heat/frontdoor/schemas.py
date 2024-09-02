import phonenumbers
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from marshmallow import Schema, ValidationError, fields, validate, validates
from phonenumbers import NumberParseException

from help_to_heat.frontdoor.consts import (
    address_field,
    benefits_field,
    contact_number_field,
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
    country_field,
    country_field_england,
    country_field_northern_ireland,
    country_field_scotland,
    country_field_wales,
    email_field,
    epc_rating_field,
    field_dont_know,
    field_no,
    field_yes,
    first_name_field,
    household_income_field,
    household_income_field_less_than_threshold,
    household_income_field_more_than_threshold,
    last_name_field,
    loft_access_field,
    loft_access_field_no,
    loft_access_field_no_loft,
    loft_access_field_yes,
    loft_field,
    loft_field_no,
    loft_field_yes,
    loft_insulation_field,
    loft_insulation_field_dont_know,
    loft_insulation_field_less_than_threshold,
    loft_insulation_field_more_than_threshold,
    loft_insulation_field_no_loft,
    number_of_bedrooms_field,
    number_of_bedrooms_field_one,
    number_of_bedrooms_field_studio,
    number_of_bedrooms_field_three_or_more,
    number_of_bedrooms_field_two,
    own_property_field,
    own_property_field_landlord,
    own_property_field_own_property,
    own_property_field_social_housing,
    own_property_field_tenant,
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
    property_type_field_park_home,
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

# page_order = (
#     "country",
#     "supplier",
#     "own-property",
#     "park-home",
#     "address",
#     "council-tax-band",
#     "epc",
#     "benefits",
#     "household-income",
#     "property-type",
#     "property-subtype",
#     "number-of-bedrooms",
#     "wall-type",
#     "wall-insulation",
#     "loft",
#     "summary",
#     "schemes",
#     "contact-details",
#     "confirm-and-submit",
#     "success",
# )
#
# page_order_park_home = (
#     "country",
#     "supplier",
#     "own-property",
#     "park-home",
#     "park-home-main-residence",
#     "address",
#     "epc",
#     "benefits",
#     "household-income",
#     "summary",
#     "schemes",
#     "contact-details",
#     "confirm-and-submit",
#     "success",
# )
#
# page_order_social_housing = (
#     "country",
#     "supplier",
#     "own-property",
#     "address",
#     "epc",
#     "property-type",
#     "property-subtype",
#     "number-of-bedrooms",
#     "wall-type",
#     "wall-insulation",
#     "loft",
#     "summary",
#     "schemes",
#     "contact-details",
#     "confirm-and-submit",
#     "success",
# )
#
# extra_pages = (
#     "applications-closed",
#     "address-select",
#     "epc-select",
#     "address-manual",
#     "loft-access",
#     "loft-insulation",
#     "northern-ireland",
#     "epc-ineligible",
#     "ineligible",
#     "bulb-warning-page",
#     "utility-warehouse-warning-page",
#     "shell-warning-page",
#     "park-home-application-closed",
#     "referral-already-submitted",
# )
#
# page_prev_next_map = {
#     "address-select": {"prev": "address", "next": "council-tax-band"},
#     "epc-select": {"prev": "address", "next": "council-tax-band"},
#     "address-manual": {"prev": "address", "next": "council-tax-band"},
#     "loft": {"prev": "wall-insulation", "next": "loft-access"},
#     "loft-access": {"prev": "loft", "next": "loft-insulation"},
#     "loft-insulation": {"prev": "loft-access", "next": "summary"},
#     "epc-ineligible": {"prev": "epc", "next": None},
#     "ineligible": {"prev": "household-income", "next": None},
#     "northern-ireland": {"prev": "country", "next": None},
#     "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
#     "utility-warehouse-warning-page": {"prev": "supplier", "next": "own-property"},
#     "shell-warning-page": {"prev": "supplier", "next": "own-property"},
#     "applications-closed": {"prev": "supplier", "next": None},
#     "benefits": {"prev": "council-tax-band", "next": "household-income"},
#     "park-home": {"prev": "own-property", "next": "address"},
#     "park-home-main-residence": {"prev": "park-home", "next": "address"},
#     "park-home-application-closed": {"prev": "park-home-main-residence", "next": None},
#     "referral-already-submitted": {"prev": "address", "next": "council-tax-band"},
# }
#
# page_prev_next_map_park_home = {
#     "address-select": {"prev": "address", "next": "epc"},
#     "epc-select": {"prev": "address", "next": "epc"},
#     "address-manual": {"prev": "address", "next": "epc"},
#     "northern-ireland": {"prev": "country", "next": None},
#     "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
#     "utility-warehouse-warning-page": {"prev": "supplier", "next": "own-property"},
#     "shell-warning-page": {"prev": "supplier", "next": "own-property"},
#     "applications-closed": {"prev": "supplier", "next": None},
#     "application-closed-utility-warehouse": {"prev": "supplier", "next": None},
#     "park-home-application-closed": {"prev": "park-home-main-residence", "next": None},
#     "epc-ineligible": {"prev": "epc", "next": None},
#     "ineligible": {"prev": "household-income", "next": None},
#     "referral-already-submitted": {"prev": "address", "next": "epc"},
# }
#
# page_prev_next_map_social_housing = {
#     "address-select": {"prev": "address", "next": "epc"},
#     "epc-select": {"prev": "address", "next": "epc"},
#     "address-manual": {"prev": "address", "next": "epc"},
#     "loft": {"prev": "wall-insulation", "next": "loft-access"},
#     "loft-access": {"prev": "loft", "next": "loft-insulation"},
#     "loft-insulation": {"prev": "loft-access", "next": "summary"},
#     "epc-ineligible": {"prev": "epc", "next": None},
#     "northern-ireland": {"prev": "country", "next": None},
#     "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
#     "utility-warehouse-warning-page": {"prev": "supplier", "next": "own-property"},
#     "shell-warning-page": {"prev": "supplier", "next": "own-property"},
#     "applications-closed": {"prev": "supplier", "next": None},
#     "referral-already-submitted": {"prev": "address", "next": "epc"},
# }

summary_map = {
    country_field: _("Country of property"),
    supplier_field: _("Energy supplier"),
    own_property_field: pgettext_lazy("summary page", "Do you own the property?"),
    park_home_field: _("Do you live in a park home?"),
    park_home_main_residence_field: _("Is the park home your main residence?"),
    address_field: _("Property address"),
    council_tax_band_field: _("Council tax band"),
    epc_rating_field: _("Energy Performance Certificate"),
    benefits_field: pgettext_lazy(
        "summary page", "Is anyone in your household receiving any of the following benefits?"
    ),
    household_income_field: _("Annual household income"),
    property_type_field: _("Property type"),
    property_subtype_field: _("Property type"),
    number_of_bedrooms_field: _("Number of bedrooms"),
    wall_type_field: _("Property walls"),
    wall_insulation_field: pgettext_lazy("summary page", "Are your walls insulated?"),
    loft_field: _("Does this property have a loft?"),
    loft_access_field: _("Is there access to your loft?"),
    loft_insulation_field: _("Is there 100mm of insulation in your loft?"),
}

confirm_sumbit_map = {
    supplier_field: _("Energy supplier"),
    first_name_field: _("First name"),
    last_name_field: _("Last name"),
    contact_number_field: _("Contact number"),
    email_field: _("Email"),
}

# household_pages = {
#     "country": ("country",),
#     "supplier": ("supplier",),
#     "bulb-warning-page": ("bulb-warning-page",),
#     "utility-warehouse-warning-page": ("utility-warehouse-warning-page",),
#     "shell-warning-page": ("shell-warning-page",),
#     "applications-closed": ("applications-closed",),
#     "own-property": ("own_property",),
#     "park-home": ("park_home",),
#     "park-home-main-residence": ("park_home_main_residence",),
#     "park-home-application-closed": ("park_home_application_closed",),
#     "address": ("address",),
#     "council-tax-band": ("council_tax_band",),
#     "epc": ("epc_rating",),
#     "benefits": ("benefits",),
#     "household-income": ("household_income",),
#     "property-type": ("property_type",),
#     "property-subtype": ("property_subtype",),
#     "number-of-bedrooms": ("number_of_bedrooms",),
#     "wall-type": ("wall_type",),
#     "wall-insulation": ("wall_insulation",),
#     "loft": ("loft",),
#     "loft-access": ("loft_access",),
#     "loft-insulation": ("loft_insulation",),
# }

# details_pages = {
#     "contact-details": ("first_name", "last_name", "contact_number", "email"),
# }

# change_page_lookup = {
#     **{page_name: "summary" for page_name in household_pages},
#     **{page_name: "confirm-and-submit" for page_name in details_pages},
# }

# question_page_lookup = {
#     question: page_name
#     for page_name, questions in itertools.chain(household_pages.items(), details_pages.items())
#     for question in questions
# }

# pages = page_order + extra_pages + page_order_park_home

country_options_map = (
    {
        "value": country_field_england,
        "label": _("England"),
    },
    {
        "value": country_field_scotland,
        "label": _("Scotland"),
    },
    {
        "value": country_field_wales,
        "label": _("Wales"),
    },
    {
        "value": country_field_northern_ireland,
        "label": _("Northern Ireland"),
    },
)

own_property_options_map = (
    {
        "value": own_property_field_own_property,
        "label": _("Yes, I own my property and live in it"),
    },
    {
        "value": own_property_field_tenant,
        "label": _("No, I am a tenant"),
        "hint": _(
            "If you are eligible for a referral through this service, your energy supplier will need to check that you \
            have your landlord’s permission to install any energy-saving measures to the property."
        ),
    },
    {
        "value": own_property_field_social_housing,
        "label": _("No, I am a social housing tenant"),
        "hint": _(
            "If you are eligible for a referral through this service, your energy supplier will need to check that you \
            have your landlord’s permission to install any energy-saving measures to the property."
        ),
    },
    {
        "value": own_property_field_landlord,
        "label": _("Yes, I am the property owner but I lease the property to one or more tenants"),
    },
)
park_home_options_map = (
    {
        "value": field_yes,
        "label": pgettext_lazy("park home question option", "Yes"),
    },
    {
        "value": field_no,
        "label": pgettext_lazy("park home question option", "No"),
    },
)
park_home_main_residence_options_map = (
    {
        "value": field_yes,
        "label": _("Yes"),
    },
    {
        "value": field_no,
        "label": _("No"),
    },
)
epc_display_options_map = (
    {
        "value": field_yes,
        "label": _("Yes"),
    },
    {
        "value": field_no,
        "label": _("No"),
    },
    {
        "value": field_dont_know,
        "label": _("I do not know"),
    },
)
epc_validation_options_map = epc_display_options_map + (
    {
        "label": _("Not found"),
        "value": "Not found",
    },
)
council_tax_band_options = (
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
)
welsh_council_tax_band_options = (
    council_tax_band_field_a,
    council_tax_band_field_b,
    council_tax_band_field_c,
    council_tax_band_field_d,
    council_tax_band_field_e,
    council_tax_band_field_f,
    council_tax_band_field_g,
    council_tax_band_field_h,
    council_tax_band_field_i,
)

yes_no_options_map = (
    {
        "value": field_yes,
        "label": pgettext_lazy("yes no question option", "Yes"),
    },
    {
        "value": field_no,
        "label": pgettext_lazy("yes no question option", "No"),
    },
)
household_income_options_map = (
    {
        "value": household_income_field_less_than_threshold,
        "label": _("Less than £31,000 a year"),
    },
    {
        "value": household_income_field_more_than_threshold,
        "label": _("£31,000 or more a year"),
    },
)
property_type_options_map = (
    {
        "value": property_type_field_house,
        "label": _("House"),
    },
    {
        "value": property_type_field_bungalow,
        "label": _("Bungalow"),
    },
    {
        "value": property_type_field_apartment,
        "label": _("Apartment, flat or maisonette"),
    },
)

property_subtype_titles_options_map = {
    "House": _("house"),
    "Bungalow": _("bungalow"),
    "Apartment, flat or maisonette": _("apartment, flat or maisonette"),
}

check_your_answers_options_map = {
    country_field: {
        country_field_england: _("England"),
        country_field_scotland: _("Scotland"),
        country_field_wales: _("Wales"),
    },
    own_property_field: {
        own_property_field_own_property: _("Yes, I own my property and live in it"),
        own_property_field_tenant: _("No, I am a tenant"),
        own_property_field_social_housing: _("No, I am a social housing tenant"),
        own_property_field_landlord: _("Yes, I am the property owner but I lease the property to one or more tenants"),
    },
    benefits_field: {
        field_yes: pgettext_lazy("yes no question option", "Yes"),
        field_no: pgettext_lazy("yes no question option", "No"),
    },
    household_income_field: {
        household_income_field_less_than_threshold: _("Less than £31,000 a year"),
        household_income_field_more_than_threshold: _("£31,000 or more a year"),
    },
    property_type_field: {
        property_type_field_house: _("House"),
        property_type_field_bungalow: _("Bungalow"),
        property_type_field_apartment: _("Apartment, flat or maisonette"),
        property_type_field_park_home: _("Park home"),
    },
    property_subtype_field: {
        property_subtype_field_detached: _("Detached"),
        property_subtype_field_semi_detached: _("Semi-detached"),
        property_subtype_field_terraced: _("Terraced"),
        property_subtype_field_end_terrace: _("End terrace"),
        property_subtype_field_top_floor: _("Top floor"),
        property_subtype_field_middle_floor: _("Middle floor"),
        property_subtype_field_ground_floor: _("Ground floor"),
    },
    number_of_bedrooms_field: {
        number_of_bedrooms_field_studio: _("Studio"),
        number_of_bedrooms_field_one: _("One bedroom"),
        number_of_bedrooms_field_two: _("Two bedrooms"),
        number_of_bedrooms_field_three_or_more: _("Three or more bedrooms"),
    },
    wall_type_field: {
        wall_type_field_solid: _("Solid walls"),
        wall_type_field_cavity: _("Cavity walls"),
        wall_type_field_mix: _("Mix of solid and cavity walls"),
        wall_type_field_not_listed: _("I do not see my option listed"),
        wall_type_field_dont_know: _("I do not know"),
    },
    wall_insulation_field: {
        wall_insulation_field_yes: _("Yes they are all insulated"),
        wall_insulation_field_some: _("Some are insulated, some are not"),
        wall_insulation_field_no: _("No they are not insulated"),
        wall_insulation_field_dont_know: _("I do not know"),
    },
    loft_field: {
        loft_field_yes: _("Yes, I have a loft that has not been converted into a room"),
        loft_field_no: _("No, I do not have a loft or my loft has been converted into a room"),
    },
    loft_access_field: {
        loft_access_field_yes: _("Yes, there is access to my loft"),
        loft_access_field_no: _("No, there is no access to my loft"),
        loft_access_field_no_loft: _("No loft"),
    },
    loft_insulation_field: {
        loft_insulation_field_more_than_threshold: _("I have more than 100mm of loft insulation"),
        loft_insulation_field_less_than_threshold: _("I have up to 100mm of loft insulation"),
        loft_insulation_field_dont_know: _("I do not know"),
        loft_insulation_field_no_loft: _("No loft"),
    },
}

property_subtype_options_map = {
    property_type_field_apartment: (
        {
            "value": property_subtype_field_top_floor,
            "label": _("Top floor"),
            "hint": _("Sits directly below the roof with no other flat above it"),
        },
        {
            "value": property_subtype_field_middle_floor,
            "label": _("Middle floor"),
            "hint": _("Has another flat above, and another below"),
        },
        {
            "value": property_subtype_field_ground_floor,
            "label": _("Ground floor"),
            "hint": _(
                "The lowest flat in the building with no flat beneath - typically at street level but may be a basement"
            ),  # noqa E501
        },
    ),
    property_type_field_bungalow: (
        {
            "value": property_subtype_field_detached,
            "label": _("Detached"),
            "hint": _("Does not share any of its walls with another house or building"),
        },
        {
            "value": property_subtype_field_semi_detached,
            "label": _("Semi-detached"),
            "hint": _("Is attached to one other house or building"),
        },
        {
            "value": property_subtype_field_terraced,
            "label": _("Terraced"),
            "hint": _("Sits in the middle with a house or building on each side"),
        },
        {
            "value": property_subtype_field_end_terrace,
            "label": _("End terrace"),
            "hint": _("Sits at the end of a row of similar houses with one house attached to it"),
        },
    ),
    property_type_field_house: (
        {
            "value": property_subtype_field_detached,
            "label": _("Detached"),
            "hint": _("Does not share any of its walls with another house or building"),
        },
        {
            "value": property_subtype_field_semi_detached,
            "label": _("Semi-detached"),
            "hint": _("Is attached to one other house or building"),
        },
        {
            "value": property_subtype_field_terraced,
            "label": _("Terraced"),
            "hint": _("Sits in the middle with a house or building on each side"),
        },
        {
            "value": property_subtype_field_end_terrace,
            "label": _("End terrace"),
            "hint": _("Sits at the end of a row of similar houses with one house attached to it"),
        },
    ),
}
number_of_bedrooms_options_map = (
    {
        "value": number_of_bedrooms_field_studio,
        "label": _("Studio"),
    },
    {
        "value": number_of_bedrooms_field_one,
        "label": _("One bedroom"),
    },
    {
        "value": number_of_bedrooms_field_two,
        "label": _("Two bedrooms"),
    },
    {
        "value": number_of_bedrooms_field_three_or_more,
        "label": _("Three or more bedrooms"),
    },
)

wall_type_options_map = (
    {
        "value": wall_type_field_solid,
        "label": _("Solid walls"),
    },
    {
        "value": wall_type_field_cavity,
        "label": _("Cavity walls"),
    },
    {
        "value": wall_type_field_mix,
        "label": _("Mix of solid and cavity walls"),
    },
    {
        "value": wall_type_field_not_listed,
        "label": _("I do not see my option listed"),
        "hint": _(
            "Other wall types could include cob walls, timber framed, system built, steel framed or other "
            "non-traditional build types"
        ),
    },
    {
        "value": wall_type_field_dont_know,
        "label": _("I do not know"),
    },
)
wall_insulation_options_map = (
    {
        "value": wall_insulation_field_yes,
        "label": _("Yes they are all insulated"),
    },
    {
        "value": wall_insulation_field_some,
        "label": _("Some are insulated, some are not"),
    },
    {
        "value": wall_insulation_field_no,
        "label": _("No they are not insulated"),
    },
    {
        "value": wall_insulation_field_dont_know,
        "label": _("I do not know"),
    },
)
loft_options_map = (
    {
        "value": loft_field_yes,
        "label": _("Yes, I have a loft that has not been converted into a room"),
    },
    {
        "value": loft_field_no,
        "label": _("No, I do not have a loft or my loft has been converted into a room"),
    },
)
loft_access_options_map = (
    {
        "value": loft_access_field_yes,
        "label": _("Yes, there is access to my loft"),
    },
    {
        "value": loft_access_field_no,
        "label": _("No, there is no access to my loft"),
    },
)
loft_access_validation_options_map = loft_access_options_map + (
    {
        "value": loft_access_field_no_loft,
        # TODO: does this mean this isn't translated?
    },
)

supplier_options = (
    {
        "value": supplier_field_british_gas,
        "label": "British Gas",
    },
    {
        "value": supplier_field_bulb,
        "label": _("Bulb, now part of Octopus Energy"),
    },
    {
        "value": supplier_field_e,
        "label": "E (Gas & Electricity) Ltd",
    },
    {
        "value": supplier_field_edf,
        "label": "EDF",
    },
    {
        "value": supplier_field_eon_next,
        "label": "E.ON Next",
    },
    {
        "value": supplier_field_foxglove,
        "label": "Foxglove",
    },
    {
        "value": supplier_field_octopus,
        "label": "Octopus Energy",
    },
    {
        "value": supplier_field_ovo,
        "label": "OVO",
    },
    {
        "value": supplier_field_scottish_power,
        "label": "Scottish Power",
    },
    {
        "value": supplier_field_shell,
        "label": "Shell",
    },
    {
        "value": supplier_field_utilita,
        "label": "Utilita",
    },
    {
        "value": supplier_field_utility_warehouse,
        "label": "Utility Warehouse",
    },
)
epc_rating_options = ("A", "B", "C", "D", "E", "F", "G", "H", "Not found")
loft_insulation_options_map = (
    {
        "value": loft_insulation_field_more_than_threshold,
        "label": _("I have more than 100mm of loft insulation"),
    },
    {
        "value": loft_insulation_field_less_than_threshold,
        "label": _("I have up to 100mm of loft insulation"),
    },
    {
        "value": loft_insulation_field_dont_know,
        "label": _("I do not know"),
    },
)
loft_insulation_validation_options_map = loft_insulation_options_map + (
    {
        "value": loft_insulation_field_no_loft,
    },
)
agreement_multichoice_options = (
    {
        "value": "Completely agree",
        "label": _("Completely agree"),
    },
    {
        "value": "Agree",
        "label": _("Agree"),
    },
    {
        "value": "Neutral",
        "label": _("Neutral"),
    },
    {
        "value": "Disagree",
        "label": _("Disagree"),
    },
    {
        "value": "Completely disagree",
        "label": _("Completely disagree"),
    },
)

satisfaction_multichoice_options = (
    {
        "value": "Very satisfied",
        "label": _("Very satisfied"),
    },
    {
        "value": "Somewhat satisfied",
        "label": _("Somewhat satisfied"),
    },
    {
        "value": "Neither satisfied nor dissatisfied",
        "label": _("Neither satisfied nor dissatisfied"),
    },
    {
        "value": "Somewhat dissatisfied",
        "label": _("Somewhat dissatisfied"),
    },
    {
        "value": "Very dissatisfied",
        "label": _("Very dissatisfied"),
    },
)

service_usage_multichoice_options = (
    {
        "value": "To find ways to reduce my energy bills",
        "label": _("To find ways to reduce my energy bills"),
    },
    {
        "value": "To find ways to reduce my carbon emissions",
        "label": _("To find ways to reduce my carbon emissions"),
    },
    {
        "value": "To find ways to install a specific measure in my home",
        "label": _("To find ways to install a specific measure in my home"),
    },
    {
        "value": "To find ways to improve my EPC rating",
        "label": _("To find ways to improve my EPC rating"),
    },
    {
        "value": "To find ways to make my home more comfortable",
        "label": _("To find ways to make my home more comfortable"),
    },
    {
        "value": "Other",
        "label": _("Other"),
    },
)


postcode_regex_collection = (
    # allow both upper and lower cases, no or multiple spaces in between outward and inward code
    r"^\s*[a-zA-Z]{1,2}\d[\da-zA-Z]?(\s*\d[a-zA-Z]{2})*\s*$"
)


all_property_types = tuple(item["value"] for item in property_type_options_map) + ("Park home",)
all_property_subtypes = tuple(item["value"] for value in property_subtype_options_map.values() for item in value) + (
    "Park home",
)


class SessionSchema(Schema):
    country = fields.String(validate=validate.OneOf(tuple(item["value"] for item in country_options_map)))
    own_property = fields.String(validate=validate.OneOf(tuple(item["value"] for item in own_property_options_map)))
    park_home = fields.String(validate=validate.OneOf(tuple(item["value"] for item in park_home_options_map)))
    park_home_main_residence = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in park_home_main_residence_options_map))
    )
    address_line_1 = fields.String(validate=validate.Length(max=128))
    address_line_2 = fields.String(validate=validate.Length(max=128))
    building_name_or_number = fields.String(validate=validate.Length(max=128))
    town_or_city = fields.String(validate=validate.Length(max=128))
    county = fields.String(validate=validate.Length(max=128))
    postcode = fields.String(
        validate=validate.Regexp(postcode_regex_collection, error=_("Please enter a valid UK postcode"))
    )
    uprn = fields.String()
    rrn = fields.String()
    epc_details = fields.Dict()
    address_and_rrn_details = fields.List(fields.Dict)
    property_main_heat_source = fields.String()
    address = fields.String(validate=validate.Length(max=512))
    council_tax_band = fields.String(validate=validate.OneOf(welsh_council_tax_band_options))
    accept_suggested_epc = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in epc_validation_options_map))
    )
    epc_rating = fields.String(validate=validate.OneOf(epc_rating_options))
    epc_date = fields.String()
    benefits = fields.String(validate=validate.OneOf(tuple(item["value"] for item in yes_no_options_map)))
    household_income = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in household_income_options_map))
    )
    property_type = fields.String(validate=validate.OneOf(all_property_types))
    property_subtype = fields.String(validate=validate.OneOf(all_property_subtypes))
    number_of_bedrooms = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in number_of_bedrooms_options_map))
    )
    wall_type = fields.String(validate=validate.OneOf(tuple(item["value"] for item in wall_type_options_map)))
    wall_insulation = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in wall_insulation_options_map))
    )
    loft = fields.String(validate=validate.OneOf(tuple(item["value"] for item in loft_options_map)))
    loft_access = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in loft_access_validation_options_map))
    )
    loft_insulation = fields.String(
        validate=validate.OneOf(tuple(item["value"] for item in loft_insulation_validation_options_map))
    )
    supplier = fields.String(validate=validate.OneOf(tuple(item["value"] for item in supplier_options)))
    user_selected_supplier = fields.String(validate=validate.OneOf(tuple(item["value"] for item in supplier_options)))
    first_name = fields.String(validate=validate.Length(max=128))
    last_name = fields.String(validate=validate.Length(max=128))
    contact_number = fields.String(validate=validate.Length(max=128))
    email = fields.String(required=False)
    confirm_bulb_warning = fields.String()
    confirm_shell_warning = fields.String()
    confirm_utility_warehouse_warning = fields.String()
    address_choice = fields.String()
    epc_select_choice = fields.String()
    address_select_choice = fields.String()
    uprn_is_duplicate = fields.String()
    epc_found = fields.String()
    epc_rating_is_eligible = fields.String()

    @validates("email")
    def validate_email(self, value):
        if value:
            validate.Email(error=_("Invalid email format"))(value)

    @validates("contact_number")
    def validate_contact_number(self, value):
        if value:
            try:
                phone_number = phonenumbers.parse(value, "GB")

                if not phonenumbers.is_possible_number(phone_number):
                    raise ValidationError(
                        [_("Enter a telephone number, like 01632 960 001, 07700 900 982 or +44 808 157 0192")]
                    )
            except NumberParseException:
                raise ValidationError(
                    [_("Enter a telephone number, like 01632 960 001, 07700 900 982 or +44 808 157 0192")]
                )

    schemes = fields.List(fields.Str())
    referral_created_at = fields.String()
    _page_name = fields.String()

    class Meta:
        ordered = True


schemes_map = {
    "ECO4": _("Energy Company Obligation 4"),
    "GBIS": _("Great British Insulation Scheme"),
}
