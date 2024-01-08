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
    """
    :param session_data:
    :return: A tuple of which schemes the person is eligible for, if any
    """
    epc_rating = session_data.get("epc_rating", "Not found")
    council_tax_band = session_data.get("council_tax_band")
    country = session_data.get("country")
    benefits = session_data.get("benefits")
    property_type = session_data.get("property_type")
    own_property = session_data.get("own_property")
    park_home_main_residence = session_data.get("park_home_main_residence", "No")
    household_income = session_data.get("household_income")

    # scenario 1
    if country not in ["England", "Scotland", "Wales"]:
        return ()

    is_in_eligible_council_band = council_tax_band in country_council_tax_bands[country]["eligible"]

    if own_property == "No, I am a social housing tenant":
        # scenario 31
        if epc_rating in ["A", "B", "C"]:
            return ()

        # scenario 32
        return "GBIS", "ECO4"

    # scenario 2, 15
    if property_type == "Park home" and park_home_main_residence == "No":
        return ()

    # scenario 3, 7, 11, 16, 20, 27
    if epc_rating in ["A", "B", "C"]:
        return ()

    # scenario 4, 8, 14, 17, 22, 24, 28
    if benefits == "Yes":
        return "GBIS", "ECO4"

    # scenario 5, 9, 12, 19, 23, 25, 29
    if household_income == "Less than £31,000 a year":
        return "GBIS", "ECO4"

    # scenario 6, 10, 18, 21, 26
    if property_type == "Park home" or is_in_eligible_council_band:
        return ("GBIS",)

    # there are no other options left other than
    # scenario 13, 30
    return ()
