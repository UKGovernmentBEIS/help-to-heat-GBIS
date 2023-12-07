import itertools

from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from marshmallow import Schema, fields, validate, validates

page_order = (
    "country",
    "supplier",
    "own-property",
    "address",
    "council-tax-band",
    "epc",
    "benefits",
    "household-income",
    "property-type",
    "property-subtype",
    "number-of-bedrooms",
    "wall-type",
    "wall-insulation",
    "loft",
    "summary",
    "schemes",
    "contact-details",
    "confirm-and-submit",
    "success",
)

page_order_park_home = (
    "country",
    "supplier",
    "own-property",
    "park-home",
    "park-home-main-residence",
    "address",
    "benefits",
    "household-income",
    "summary",
    "schemes",
    "contact-details",
    "confirm-and-submit",
    "success",
)

extra_pages = (
    "applications-closed",
    "address-select",
    "epc-select",
    "address-manual",
    "loft-access",
    "loft-insulation",
    "northern-ireland",
    "epc-ineligible",
    "ineligible",
    "bulb-warning-page",
    "utility-warehouse-warning-page",
    "park-home-application-closed",
)

page_prev_next_map = {
    "address-select": {"prev": "address", "next": "council-tax-band"},
    "epc-select": {"prev": "address", "next": "council-tax-band"},
    "address-manual": {"prev": "address", "next": "council-tax-band"},
    "loft": {"prev": "wall-insulation", "next": "loft-access"},
    "loft-access": {"prev": "loft", "next": "loft-insulation"},
    "loft-insulation": {"prev": "loft-access", "next": "summary"},
    "epc-ineligible": {"prev": "epc", "next": None},
    "ineligible": {"prev": "benefits", "next": None},
    "northern-ireland": {"prev": "country", "next": None},
    "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
    "utility-warehouse-warning-page": {"prev": "supplier", "next": "own-property"},
    "applications-closed": {"prev": "supplier", "next": None},
    "benefits": {"prev": "council-tax-band", "next": "household-income"},
    "park-home": {"prev": "own-property", "next": "address"},
    "park-home-main-residence": {"prev": "park-home", "next": "address"},
    "park-home-application-closed": {"prev": "park-home-main-residence", "next": None},
}

page_prev_next_map_park_home = {
    "address-select": {"prev": "address", "next": "benefits"},
    "epc-select": {"prev": "address", "next": "benefits"},
    "address-manual": {"prev": "address", "next": "benefits"},
    "northern-ireland": {"prev": "country", "next": None},
    "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
    "utility-warehouse-warning-page": {"prev": "supplier", "next": "own-property"},
    "applications-closed": {"prev": "supplier", "next": None},
    "application-closed-utility-warehouse": {"prev": "supplier", "next": None},
    "park-home-application-closed": {"prev": "park-home-main-residence", "next": None},
}

summary_map = {
    "country": _("Country of property"),
    "supplier": _("Energy supplier"),
    "own_property": pgettext_lazy("summary page", "Do you own the property?"),
    "park_home": _("Do you live in a park home?"),
    "park_home_main_residence": _("Is the park home your main residence?"),
    "address": _("Property address"),
    "council_tax_band": _("Council tax band"),
    "epc_rating": _("Energy Performance Certificate"),
    "benefits": pgettext_lazy("summary page", "Is anyone in your household receiving any of the following benefits?"),
    "household_income": _("Annual household income"),
    "property_type": _("Property type"),
    "property_subtype": _("Property type"),
    "number_of_bedrooms": _("Number of bedrooms"),
    "wall_type": _("Property walls"),
    "wall_insulation": pgettext_lazy("summary page", "Are your walls insulated?"),
    "loft": _("Does this property have a loft?"),
    "loft_access": _("Is there access to your loft?"),
    "loft_insulation": _("Is there 270mm of insulation in your loft?"),
}

confirm_sumbit_map = {
    "supplier": _("Energy supplier"),
    "first_name": _("First name"),
    "last_name": _("Last name"),
    "contact_number": _("Mobile number"),
    "email": _("Email"),
}

household_pages = {
    "country": ("country",),
    "supplier": ("supplier",),
    "bulb-warning-page": ("bulb-warning-page",),
    "utility-warehouse-warning-page": ("utility-warehouse-warning-page",),
    "applications-closed": ("applications-closed",),
    "own-property": ("own_property",),
    "park-home": ("park_home",),
    "park-home-main-residence": ("park_home_main_residence",),
    "park-home-application-closed": ("park_home_application_closed",),
    "address": ("address",),
    "council-tax-band": ("council_tax_band",),
    "epc": ("epc_rating",),
    "benefits": ("benefits",),
    "household-income": ("household_income",),
    "property-type": ("property_type",),
    "property-subtype": ("property_subtype",),
    "number-of-bedrooms": ("number_of_bedrooms",),
    "wall-type": ("wall_type",),
    "wall-insulation": ("wall_insulation",),
    "loft": ("loft",),
    "loft-access": ("loft_access",),
    "loft-insulation": ("loft_insulation",),
}

details_pages = {
    "contact-details": ("first_name", "last_name", "contact_number", "email"),
}

change_page_lookup = {
    **{page_name: "summary" for page_name in household_pages},
    **{page_name: "confirm-and-submit" for page_name in details_pages},
}

question_page_lookup = {
    question: page_name
    for page_name, questions in itertools.chain(household_pages.items(), details_pages.items())
    for question in questions
}

pages = page_order + extra_pages + page_order_park_home

country_options_map = (
    {
        "value": "England",
        "label": _("England"),
    },
    {
        "value": "Scotland",
        "label": _("Scotland"),
    },
    {
        "value": "Wales",
        "label": _("Wales"),
    },
    {
        "value": "Northern Ireland",
        "label": _("Northern Ireland"),
    },
)

own_property_options_map = (
    {
        "value": "Yes, I own my property and live in it",
        "label": _("Yes, I own my property and live in it"),
    },
    {
        "value": "No, I am a tenant",
        "label": _("No, I am a tenant"),
        "hint": _(
            "If you are eligible for a referral through this service, your energy supplier will need to check that you \
            have your landlord’s permission to install any energy-saving measures to the property."
        ),
    },
    {
        "value": "No, I am a social housing tenant",
        "label": _("No, I am a social housing tenant"),
        "hint": _(
            "If you are eligible for a referral through this service, your energy supplier will need to check that you \
            have your landlord’s permission to install any energy-saving measures to the property."
        ),
    },
    {
        "value": "Yes, I am the property owner but I lease the property to one or more tenants",
        "label": _("Yes, I am the property owner but I lease the property to one or more tenants"),
    },
)
park_home_options_map = (
    {
        "value": "Yes",
        "label": pgettext_lazy("park home question option", "Yes"),
    },
    {
        "value": "No",
        "label": pgettext_lazy("park home question option", "No"),
    },
)
park_home_main_residence_options_map = (
    {
        "value": "Yes",
        "label": _("Yes"),
    },
    {
        "value": "No",
        "label": _("No"),
    },
)
epc_display_options_map = (
    {
        "value": "Yes",
        "label": _("Yes"),
    },
    {
        "value": "No",
        "label": _("No"),
    },
    {
        "value": "I don't know",
        "label": _("I don't know"),
    },
)
epc_validation_options_map = epc_display_options_map + (
    {
        "label": _("Not found"),
        "value": "Not found",
    },
)
council_tax_band_options = ("A", "B", "C", "D", "E", "F", "G", "H")
welsh_council_tax_band_options = ("A", "B", "C", "D", "E", "F", "G", "H", "I")

yes_no_options_map = (
    {
        "value": "Yes",
        "label": pgettext_lazy("yes no question option", "Yes"),
    },
    {
        "value": "No",
        "label": pgettext_lazy("yes no question option", "No"),
    },
)
household_income_options_map = (
    {
        "value": "Less than £31,000 a year",
        "label": _("Less than £31,000 a year"),
    },
    {
        "value": "£31,000 or more a year",
        "label": _("£31,000 or more a year"),
    },
)
property_type_options_map = (
    {
        "value": "House",
        "label": _("House"),
    },
    {
        "value": "Bungalow",
        "label": _("Bungalow"),
    },
    {
        "value": "Apartment, flat or maisonette",
        "label": _("Apartment, flat or maisonette"),
    },
)

property_subtype_titles_options_map = {
    "House": _("house"),
    "Bungalow": _("bungalow"),
    "Apartment, flat or maisonette": _("apartment, flat or maisonette"),
}

check_your_answers_options_map = {
    "country": {
        "England": _("England"),
        "Scotland": _("Scotland"),
        "Wales": _("Wales"),
    },
    "own_property": {
        "Yes, I own my property and live in it": _("Yes, I own my property and live in it"),
        "No, I am a tenant": _("No, I am a tenant"),
        "No, I am a social housing tenant": _("No, I am a social housing tenant"),
        "Yes, I am the property owner but I lease the property to one or more tenants": _(
            "Yes, I am the property owner but I lease the property to one or more tenants"
        ),
    },
    "benefits": {
        "Yes": pgettext_lazy("yes no question option", "Yes"),
        "No": pgettext_lazy("yes no question option", "No"),
    },
    "household_income": {
        "Less than £31,000 a year": _("Less than £31,000 a year"),
        "£31,000 or more a year": _("£31,000 or more a year"),
    },
    "property_type": {
        "House": _("House"),
        "Bungalow": _("Bungalow"),
        "Apartment, flat or maisonette": _("Apartment, flat or maisonette"),
        "Park home": _("Park home"),
    },
    "property_subtype": {
        "Detached": _("Detached"),
        "Semi-detached": _("Semi-detached"),
        "Terraced": _("Terraced"),
        "End terrace": _("End terrace"),
        "Top floor": _("Top floor"),
        "Middle floor": _("Middle floor"),
        "Ground floor": _("Ground floor"),
    },
    "number_of_bedrooms": {
        "Studio": _("Studio"),
        "One bedroom": _("One bedroom"),
        "Two bedrooms": _("Two bedrooms"),
        "Three or more bedrooms": _("Three or more bedrooms"),
    },
    "wall_type": {
        "Solid walls": _("Solid walls"),
        "Cavity walls": _("Cavity walls"),
        "Mix of solid and cavity walls": _("Mix of solid and cavity walls"),
        "I don't see my option listed": _("I don't see my option listed"),
        "I don't know": _("I don't know"),
    },
    "wall_insulation": {
        "Yes they are all insulated": _("Yes they are all insulated"),
        "Some are insulated, some are not": _("Some are insulated, some are not"),
        "No they are not insulated": _("No they are not insulated"),
        "I don't know": _("I don't know"),
    },
    "loft": {
        "Yes, I have a loft that hasn't been converted into a room": _(
            "Yes, I have a loft that hasn't been converted into a room"
        ),
        "No, I don't have a loft or my loft has been converted into a room": _(
            "No, I don't have a loft or my loft has been converted into a room"
        ),
    },
    "loft_access": {
        "Yes, there is access to my loft": _("Yes, there is access to my loft"),
        "No, there is no access to my loft": _("No, there is no access to my loft"),
        "No loft": _("No loft"),
    },
    "loft_insulation": {
        "Yes, there is at least 270mm of insulation in my loft": _(
            "Yes, there is at least 270mm of insulation in my loft"
        ),
        "No, there is less than 270mm of insulation in my loft": _(
            "No, there is less than 270mm of insulation in my loft"
        ),
        "I don't know": _("I don't know"),
        "No loft": _("No loft"),
    },
}

property_subtype_options_map = {
    "Apartment, flat or maisonette": (
        {
            "value": "Top floor",
            "label": _("Top floor"),
            "hint": _("Sits directly below the roof with no other flat above it"),
        },
        {
            "value": "Middle floor",
            "label": _("Middle floor"),
            "hint": _("Has another flat above, and another below"),
        },
        {
            "value": "Ground floor",
            "label": _("Ground floor"),
            "hint": _(
                "The lowest flat in the building with no flat beneath - typically at street level but may be a basement"
            ),  # noqa E501
        },
    ),
    "Bungalow": (
        {
            "value": "Detached",
            "label": _("Detached"),
            "hint": _("Does not share any of its walls with another house or building"),
        },
        {
            "value": "Semi-detached",
            "label": _("Semi-detached"),
            "hint": _("Is attached to one other house or building"),
        },
        {
            "value": "Terraced",
            "label": _("Terraced"),
            "hint": _("Sits in the middle with a house or building on each side"),
        },
        {
            "value": "End terrace",
            "label": _("End terrace"),
            "hint": _("Sits at the end of a row of similar houses with one house attached to it"),
        },
    ),
    "House": (
        {
            "value": "Detached",
            "label": _("Detached"),
            "hint": _("Does not share any of its walls with another house or building"),
        },
        {
            "value": "Semi-detached",
            "label": _("Semi-detached"),
            "hint": _("Is attached to one other house or building"),
        },
        {
            "value": "Terraced",
            "label": _("Terraced"),
            "hint": _("Sits in the middle with a house or building on each side"),
        },
        {
            "value": "End terrace",
            "label": _("End terrace"),
            "hint": _("Sits at the end of a row of similar houses with one house attached to it"),
        },
    ),
}
number_of_bedrooms_options_map = (
    {
        "value": "Studio",
        "label": _("Studio"),
    },
    {
        "value": "One bedroom",
        "label": _("One bedroom"),
    },
    {
        "value": "Two bedrooms",
        "label": _("Two bedrooms"),
    },
    {
        "value": "Three or more bedrooms",
        "label": _("Three or more bedrooms"),
    },
)

wall_type_options_map = (
    {
        "value": "Solid walls",
        "label": _("Solid walls"),
    },
    {
        "value": "Cavity walls",
        "label": _("Cavity walls"),
    },
    {
        "value": "Mix of solid and cavity walls",
        "label": _("Mix of solid and cavity walls"),
    },
    {
        "value": "I don't see my option listed",
        "label": _("I don't see my option listed"),
        "hint": _(
            "Other wall types could include cob walls, timber framed, system built, steel framed or other "
            "non-traditional build types"
        ),
    },
    {
        "value": "I don't know",
        "label": _("I don't know"),
    },
)
wall_insulation_options_map = (
    {
        "value": "Yes they are all insulated",
        "label": _("Yes they are all insulated"),
    },
    {
        "value": "Some are insulated, some are not",
        "label": _("Some are insulated, some are not"),
    },
    {
        "value": "No they are not insulated",
        "label": _("No they are not insulated"),
    },
    {
        "value": "I don't know",
        "label": _("I don't know"),
    },
)
loft_options_map = (
    {
        "value": "Yes, I have a loft that hasn't been converted into a room",
        "label": _("Yes, I have a loft that hasn't been converted into a room"),
    },
    {
        "value": "No, I don't have a loft or my loft has been converted into a room",
        "label": _("No, I don't have a loft or my loft has been converted into a room"),
    },
)
loft_access_options_map = (
    {
        "value": "Yes, there is access to my loft",
        "label": _("Yes, there is access to my loft"),
    },
    {
        "value": "No, there is no access to my loft",
        "label": _("No, there is no access to my loft"),
    },
)
loft_access_validation_options_map = loft_access_options_map + (
    {
        "value": "No loft",
    },
)

supplier_options = (
    {
        "label": "British Gas",
        "value": "British Gas",
    },
    {
        "value": "Bulb, now part of Octopus Energy",
        "label": _("Bulb, now part of Octopus Energy"),
    },
    {
        "label": "E (Gas & Electricity) Ltd",
        "value": "E (Gas & Electricity) Ltd",
    },
    {
        "label": "Ecotricity",
        "value": "Ecotricity",
    },
    {
        "label": "EDF",
        "value": "EDF",
    },
    {
        "label": "E.ON Next",
        "value": "E.ON Next",
    },
    {
        "label": "Foxglove",
        "value": "Foxglove",
    },
    {
        "label": "Octopus Energy",
        "value": "Octopus Energy",
    },
    {
        "label": "OVO",
        "value": "OVO",
    },
    {
        "label": "Scottish Power",
        "value": "Scottish Power",
    },
    {
        "label": "Shell",
        "value": "Shell",
    },
    {
        "label": "So Energy",
        "value": "So Energy",
    },
    {
        "label": "Utilita",
        "value": "Utilita",
    },
    {
        "label": "Utility Warehouse",
        "value": "Utility Warehouse",
    },
)
epc_rating_options = ("A", "B", "C", "D", "E", "F", "G", "H", "Not found")
loft_insulation_options_map = (
    {
        "value": "Yes, there is at least 270mm of insulation in my loft",
        "label": _("Yes, there is at least 270mm of insulation in my loft"),
    },
    {
        "value": "No, there is less than 270mm of insulation in my loft",
        "label": _("No, there is less than 270mm of insulation in my loft"),
    },
    {
        "value": "I don't know",
        "label": _("I don't know"),
    },
)
loft_insulation_validation_options_map = loft_insulation_options_map + (
    {
        "value": "No loft",
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

# allow only numbers, spaces and +.
phone_number_regex = r"^[\d\s\+]*$"


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
    contact_number = fields.String(
        validate=validate.And(
            validate.Length(max=128), validate.Regexp(phone_number_regex, error=_("Invalid contact number"))
        )
    )
    email = fields.String(required=False)

    @validates("email")
    def validate_email(self, value):
        if value:
            validate.Email(error=_("Invalid email format"))(value)

    schemes = fields.List(fields.Str())
    referral_created_at = fields.String()
    _page_name = fields.String()

    class Meta:
        ordered = True


schemes_map = {
    "ECO4": _("Energy Company Obligation 4"),
    "GBIS": _("Great British Insulation Scheme"),
}
