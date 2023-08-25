import itertools

from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from marshmallow import Schema, ValidationError, fields, validate

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

extra_pages = (
    "applications-closed",
    "address-select",
    "address-manual",
    "epc-disagree",
    "loft-access",
    "loft-insulation",
    "northern-ireland",
    "epc-ineligible",
    "ineligible",
    "bulb-warning-page",
)

page_prev_next_map = {
    "address-select": {"prev": "address", "next": "council-tax-band"},
    "address-manual": {"prev": "address", "next": "council-tax-band"},
    "epc-disagree": {"prev": "address", "next": "benefits"},
    "loft": {"prev": "wall-insulation", "next": "loft-access"},
    "loft-access": {"prev": "loft", "next": "loft-insulation"},
    "loft-insulation": {"prev": "loft-access", "next": "summary"},
    "epc-ineligible": {"prev": "epc", "next": None},
    "ineligible": {"prev": "benefits", "next": None},
    "northern-ireland": {"prev": "country", "next": None},
    "bulb-warning-page": {"prev": "supplier", "next": "own-property"},
    "applications-closed": {"prev": "supplier", "next": None},
}

summary_map = {
    "country": _("Country of property"),
    "supplier": _("Energy supplier"),
    "own_property": pgettext_lazy("summary page", "Do you own the property?"),
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
    "contact_number": "Mobile number",
    "email": _("Email"),
}

household_pages = {
    "country": ("country",),
    "supplier": ("supplier",),
    "bulb-warning-page": ("bulb-warning-page",),
    "applications-closed": ("applications-closed",),
    "own-property": ("own_property",),
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

pages = page_order + extra_pages

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
    "British Gas",
    "Bulb, now part of Octopus Energy",
    "E (Gas & Electricity) Ltd",
    "Ecotricity",
    "EDF",
    "E.ON Next",
    "Foxglove",
    "Octopus Energy",
    "OVO",
    "Scottish Power",
    "Shell",
    "So Energy",
    "Utilita",
    "Utility Warehouse",
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
multichoice_options = (
    "Completely disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Completely agree",
    "Not sure / not applicable",
)


def validate_email_or_none(value):
    if value != "" and not validate.Email()(value):
        raise ValidationError("Invalid email format")


postcode_regex_collection = (
    # allow both upper and lower cases, no or multiple spaces in between outward and inward code
    r"^[a-zA-Z]{1,2}\d[\da-zA-Z]?(\s*\d[a-zA-Z]{2})*$"
)

# allow only numbers, spaces and +.
phone_number_regex = r"^[\d\s\+]*$"


class SessionSchema(Schema):
    country = fields.String(validate=validate.OneOf(tuple(item["value"] for item in country_options_map)))
    own_property = fields.String(validate=validate.OneOf(tuple(item["value"] for item in own_property_options_map)))
    address_line_1 = fields.String(validate=validate.Length(max=128))
    address_line_2 = fields.String(validate=validate.Length(max=128))
    building_name_or_number = fields.String(validate=validate.Length(max=128))
    town_or_city = fields.String(validate=validate.Length(max=128))
    county = fields.String(validate=validate.Length(max=128))
    postcode = fields.String(
        validate=validate.Regexp(postcode_regex_collection, error="Please enter a valid UK postcode")
    )
    uprn = fields.Integer()
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
    property_type = fields.String(validate=validate.OneOf(tuple(item["value"] for item in property_type_options_map)))
    property_subtype = fields.String(
        validate=validate.OneOf(
            tuple(item["value"] for value in property_subtype_options_map.values() for item in value)
        )
    )
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
    supplier = fields.String(validate=validate.OneOf(supplier_options))
    first_name = fields.String(validate=validate.Length(max=128))
    last_name = fields.String(validate=validate.Length(max=128))
    contact_number = fields.String(
        validate=validate.And(
            validate.Length(max=128), validate.Regexp(phone_number_regex, error="please enter a contact number")
        )
    )
    email = fields.String(validate=(validate_email_or_none, validate.Length(max=128)), allow_none=True)
    schemes = fields.List(fields.Str())
    referral_created_at = fields.String()
    _page_name = fields.String()

    class Meta:
        ordered = True


schemes_map = {
    "ECO4": "Energy Company Obligation 4",
    "GBIS": "Great British Insulation Scheme",
}
