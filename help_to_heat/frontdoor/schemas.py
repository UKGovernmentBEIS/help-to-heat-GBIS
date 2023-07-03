import itertools

from marshmallow import Schema, ValidationError, fields, validate

page_order = (
    "country",
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
    "supplier",
    "contact-details",
    "confirm-and-submit",
    "success",
)

extra_pages = (
    "address-select",
    "address-manual",
    "epc-disagree",
    "loft-access",
    "loft-insulation",
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
}

summary_map = {
    "country": "Country of property",
    "own_property": "Do you own the property?",
    "address": "Property address",
    "council_tax_band": "Council tax band",
    "epc": "Energy Performance Certificate",
    "benefits": "Is anyone in your household receiving any of the following benefits?",
    "household_income": "Annual household income",
    "property_type": "Property type",
    "property_subtype": "Property type",
    "number_of_bedrooms": "Number of bedrooms",
    "wall_type": "Property walls",
    "wall_insulation": "Are your walls insulated?",
    "loft": "Does this property have a loft?",
    "loft_access": "Is there access to your loft?",
    "loft_insulation": "Is there 270mm of insulation in your loft?",
}

confirm_sumbit_map = {
    "supplier": "Energy supplier",
    "first_name": "First name",
    "last_name": "Last name",
    "contact_number": "Contact number",
    "email": "Email",
}

household_pages = {
    "country": ("country",),
    "own-property": ("own_property",),
    "address": ("address",),
    "council-tax-band": ("council_tax_band",),
    "epc": ("epc",),
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
    "supplier": ("supplier",),
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

country_options = ("England", "Scotland", "Wales", "Northern Ireland")
own_property_options_map = (
    {
        "value": "Yes, I own my property and live in it",
        "label": "Yes, I own my property and live in it",
    },
    {
        "value": "No, I am a tenant",
        "label": "No, I am a tenant",
        "hint": "If you are eligible for a referral through this service, your energy supplier will need to check that you have your landlord’s permission to install any energy-saving measures to the property.",  # noqa E501
    },
    {
        "value": "No, I am a social housing tenant",
        "label": "No, I am a social housing tenant",
        "hint": "If you are eligible for a referral through this service, your energy supplier will need to check that you have your landlord’s permission to install any energy-saving measures to the property.",  # noqa E501
    },
    {
        "value": "Yes, I am the property owner but I lease the property to one or more tenants",
        "label": "Yes, I am the property owner but I lease the property to one or more tenants",
    },
)
epc_display_options = ("Yes", "No", "I don't know")
epc_validation_options = epc_display_options + ("Not found",)
council_tax_band_options = ("A", "B", "C", "D", "E", "F", "G", "H")
welsh_council_tax_band_options = ("A", "B", "C", "D", "E", "F", "G", "H", "I")
yes_no_options = ("Yes", "No")
household_income_options = ("Less than £31,000 a year", "£31,000 or more a year")
property_type_options = ("House", "Bungalow", "Apartment, flat or maisonette")
property_subtype_options_map = {
    "Apartment, flat or maisonette": (
        {
            "value": "Top floor",
            "label": "Top floor",
            "hint": "Sits directly below the roof with no other flat above it",
        },
        {
            "value": "Middle floor",
            "label": "Middle floor",
            "hint": "Has another flat above, and another below",
        },
        {
            "value": "Ground floor",
            "label": "Ground floor",
            "hint": "The lowest flat in the building with no flat beneath - typically at street level but may be a basement",  # noqa E501
        },
    ),
    "Bungalow": (
        {
            "value": "Detached",
            "label": "Detached",
            "hint": "Does not share any of its walls with another house or building",
        },
        {
            "value": "Semi-detached",
            "label": "Semi-detached",
            "hint": "Is attached to one other house or building",
        },
        {
            "value": "Terraced",
            "label": "Terraced",
            "hint": "Sits in the middle with a house or building on each side",
        },
        {
            "value": "End Terrace",
            "label": "End terrace",
            "hint": "Sits at the end of a row of similar houses with one house attached to it",
        },
    ),
    "House": (
        {
            "value": "Detached",
            "label": "Detached",
            "hint": "Does not share any of its walls with another house or building",
        },
        {
            "value": "Semi-detached",
            "label": "Semi-detached",
            "hint": "Is attached to one other house or building",
        },
        {
            "value": "Terraced",
            "label": "Terraced",
            "hint": "Sits in the middle with a house or building on each side",
        },
        {
            "value": "End terrace",
            "label": "End terrace",
            "hint": "Sits at the end of a row of similar houses with one house attached to it",
        },
    ),
}
number_of_bedrooms_options = ("Studio", "One bedroom", "Two bedrooms", "Three or more bedrooms")
wall_type_options = (
    "Solid walls",
    "Cavity walls",
    "Mix of solid and cavity walls",
    "I don't see my option listed",
    "I don't know",
)
wall_insulation_options = (
    "Yes they are all insulated",
    "Some are insulated, some are not",
    "No they are not insulated",
    "I don't know",
)
loft_options = (
    "Yes, I have a loft that hasn't been converted into a room",
    "No, I don't have a loft or my loft has been converted into a room",
)
loft_access_options = ("Yes, there is access to my loft", "No, there is no access to my loft")
loft_access_validation_options = loft_access_options + ("No loft",)
supplier_options = (
    "British Gas",
    # "Bulb",
    # "E Energy",
    # "Ecotricity",
    "EDF",
    "EON",
    # "ESB",
    # "Foxglove",
    # "Octopus",
    "OVO",
    "Scottish Power",
    # "Shell",
    "So Energy",
    "Utilita",
    # "Utility Warehouse",
)
epc_rating_options = ("A", "B", "C", "D", "E", "F", "G", "H", "Not found")
loft_insulation_options = (
    "Yes, there is at least 270mm of insulation in my loft",
    "No, there is less than 270mm of insulation in my loft",
    "I don't know",
)
loft_insulation_validation_options = loft_insulation_options + ("No loft",)
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


class SessionSchema(Schema):
    country = fields.String(validate=validate.OneOf(country_options))
    own_property = fields.String(validate=validate.OneOf(tuple(item["value"] for item in own_property_options_map)))
    address_line_1 = fields.String()
    address_line_2 = fields.String()
    town_or_city = fields.String()
    county = fields.String()
    postcode = fields.String()
    uprn = fields.Integer()
    address = fields.String()
    council_tax_band = fields.String(validate=validate.OneOf(welsh_council_tax_band_options))
    accept_suggested_epc = fields.String(validate=validate.OneOf(epc_validation_options))
    epc_rating = fields.String(validate=validate.OneOf(epc_rating_options))
    epc_date = fields.String()
    benefits = fields.String(validate=validate.OneOf(yes_no_options))
    household_income = fields.String(validate=validate.OneOf(household_income_options))
    property_type = fields.String(validate=validate.OneOf(property_type_options))
    property_subtype = fields.String(
        validate=validate.OneOf(
            tuple(item["value"] for value in property_subtype_options_map.values() for item in value)
        )
    )
    number_of_bedrooms = fields.String(validate=validate.OneOf(number_of_bedrooms_options))
    wall_type = fields.String(validate=validate.OneOf(wall_type_options))
    wall_insulation = fields.String(validate=validate.OneOf(wall_insulation_options))
    loft = fields.String(validate=validate.OneOf(loft_options))
    loft_access = fields.String(validate=validate.OneOf(loft_access_validation_options))
    loft_insulation = fields.String(validate=validate.OneOf(loft_insulation_validation_options))
    supplier = fields.String(validate=validate.OneOf(supplier_options))
    first_name = fields.String()
    last_name = fields.String()
    contact_number = fields.String()
    email = fields.String(validate=validate_email_or_none, allow_none=True)
    schemes = fields.List(fields.Str())

    class Meta:
        ordered = True


schemes_map = {
    "ECO4": "Energy Company Obligation 4",
    "GBIS": "Great British Insulation Scheme",
}
