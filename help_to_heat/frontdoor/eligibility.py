import logging

logger = logging.getLogger(__name__)

gbis = "GBIS"
eco4 = "ECO4"

not_eligible = ()
eligible_for_gbis = (gbis,)
eligible_for_gbis_and_eco4 = (gbis, eco4)


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
        return not_eligible

    if epc_rating in ("A", "B", "C"):
        return not_eligible

    if own_property == "No, I am a social housing tenant":
        return eligible_for_gbis_and_eco4

    if property_type == "Park home" and park_home_main_residence == "No":
        return not_eligible

    if benefits == "Yes":
        return eligible_for_gbis_and_eco4

    if household_income == "Less than £31,000 a year":
        return eligible_for_gbis_and_eco4

    if property_type == "Park home":
        return eligible_for_gbis

    if _is_eligible_council_tax_band(country, council_tax_band):
        return eligible_for_gbis

    return not_eligible
