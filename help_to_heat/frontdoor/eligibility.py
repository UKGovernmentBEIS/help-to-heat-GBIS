import logging

logger = logging.getLogger(__name__)

country_council_tax_bands = {
    "England": {
        "eligible": ("A", "B", "C", "D"),
        "ineligible": ("E", "F", "G", "H"),
    },
    "Scotland": {
        "eligible": ("A", "B", "C", "D", "E"),
        "ineligible": ("F", "G", "H"),
    },
    "Wales": {
        "eligible": ("A", "B", "C", "D", "E"),
        "ineligible": ("F", "G", "H", "I"),
    },
}


def calculate_eligibility(session_data):
    epc_rating = session_data.get("epc_rating", "Not found")
    council_tax_band = session_data.get("council_tax_band")
    country = session_data.get("country")
    benefits = session_data.get("benefits")
    property_type = session_data.get("property_type")
    own_property = session_data.get("own_property")
    park_home_main_residence = session_data.get("park_home_main_residence", "No")
    household_income = session_data.get("household_income")

    if country not in ["England", "Scotland", "Wales"]:
        return ()

    is_in_eligible_council_band = council_tax_band in country_council_tax_bands[country]["eligible"]

    if own_property == "No, I am a social housing tenant":
        if epc_rating in ["A", "B", "C"]:
            return ()

        return "GBIS", "ECO4"

    if property_type == "Park home" and park_home_main_residence == "No":
        return ()

    if epc_rating in ["A", "B", "C"]:
        return ()

    if benefits == "Yes":
        return "GBIS", "ECO4"

    if household_income == "Less than £31,000 a year":
        return "GBIS", "ECO4"

    if property_type == "Park home" or is_in_eligible_council_band:
        return ("GBIS",)

    return ()
