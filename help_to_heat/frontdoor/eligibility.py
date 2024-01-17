import logging

logger = logging.getLogger(__name__)

def _is_eligible_council_tax_band(country, council_tax_band):
    if country == "England":
        return council_tax_band in ("A", "B", "C", "D")
    if country in ("Scotland", "Wales"):
        return council_tax_band in ("A", "B", "C", "D", "E")
    return False


def calculate_eligibility(session_data):
    epc_rating = session_data.get("epc_rating", "Not found")
    council_tax_band = session_data.get("council_tax_band")
    country = session_data.get("country")
    benefits = session_data.get("benefits")
    property_type = session_data.get("property_type")
    own_property = session_data.get("own_property")
    park_home_main_residence = session_data.get("park_home_main_residence", "No")
    household_income = session_data.get("household_income")

    if country not in ("England", "Scotland", "Wales"):
        return ()

    if epc_rating in ("A", "B", "C"):
        return ()

    if own_property == "No, I am a social housing tenant":
        return "GBIS", "ECO4"

    if property_type == "Park home" and park_home_main_residence == "No":
        return ()

    if benefits == "Yes":
        return "GBIS", "ECO4"

    if household_income == "Less than £31,000 a year":
        return "GBIS", "ECO4"

    if property_type == "Park home":
        return ("GBIS",)

    if _is_eligible_council_tax_band(country, council_tax_band):
        return ("GBIS",)

    return ()
