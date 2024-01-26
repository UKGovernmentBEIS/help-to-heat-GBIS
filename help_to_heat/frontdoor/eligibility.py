gbis = "GBIS"
eco4 = "ECO4"

not_eligible = ()
eligible_for_gbis = (gbis,)
eligible_for_gbis_and_eco4 = (gbis, eco4)
needs_more_information = None


def _council_tax_band_is_defined(council_tax_band):
    return council_tax_band in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "Not found")


def _is_eligible_council_tax_band(country, council_tax_band):
    if country == "England":
        return council_tax_band in ("A", "B", "C", "D")
    if country in ("Scotland", "Wales"):
        return council_tax_band in ("A", "B", "C", "D", "E")
    return False


def calculate_eligibility(session_data):
    country = session_data.get("country")
    own_property = session_data.get("own_property")
    property_type = session_data.get("property_type")
    park_home_main_residence = session_data.get("park_home_main_residence")
    council_tax_band = session_data.get("council_tax_band")
    epc_rating = session_data.get("epc_rating", "Not found")
    accept_suggested_epc = session_data.get("accept_suggested_epc")
    benefits = session_data.get("benefits")
    household_income = session_data.get("household_income")

    if country not in ("England", "Scotland", "Wales"):
        return not_eligible

    if own_property == "No, I am a social housing tenant":
        if epc_rating in ("A", "B", "C") and accept_suggested_epc == "Yes":
            return not_eligible
        return eligible_for_gbis_and_eco4

    if property_type == "Park home" and park_home_main_residence == "No":
        return not_eligible

    if epc_rating in ("A", "B", "C") and accept_suggested_epc == "Yes":
        return not_eligible

    if benefits == "Yes":
        return eligible_for_gbis_and_eco4

    if household_income == "Less than £31,000 a year":
        return eligible_for_gbis_and_eco4

    # if this is true, the form must be fully filled
    if household_income == "£31,000 or more a year" and _council_tax_band_is_defined(council_tax_band):
        if property_type == "Park home":
            return eligible_for_gbis

        if _is_eligible_council_tax_band(country, council_tax_band):
            return eligible_for_gbis

        return not_eligible

    return needs_more_information
