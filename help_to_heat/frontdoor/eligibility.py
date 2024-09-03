from help_to_heat.frontdoor.consts import country_field, own_property_field, park_home_field, field_yes, \
    park_home_main_residence_field, council_tax_band_field, field_no, epc_rating_field, epc_rating_field_not_found, \
    epc_accept_suggested_epc_field, benefits_field, household_income_field, country_field_england, \
    country_field_scotland, country_field_wales, own_property_field_social_housing, \
    household_income_field_less_than_threshold

gbis = "GBIS"
eco4 = "ECO4"

not_eligible = ()
eligible_for_gbis = (gbis,)
eligible_for_gbis_and_eco4 = (gbis, eco4)


def _is_eligible_council_tax_band(country, council_tax_band):
    if country == country_field_england:
        return council_tax_band in ("A", "B", "C", "D")
    if country in (country_field_scotland, country_field_wales):
        return council_tax_band in ("A", "B", "C", "D", "E")
    return False


def calculate_eligibility(session_data):
    country = session_data.get(country_field)
    own_property = session_data.get(own_property_field)
    park_home = session_data.get(park_home_field)
    park_home_main_residence = session_data.get(park_home_main_residence_field, field_no)
    council_tax_band = session_data.get(council_tax_band_field)
    epc_rating = session_data.get(epc_rating_field, epc_rating_field_not_found)
    accept_suggested_epc = session_data.get(epc_accept_suggested_epc_field)
    benefits = session_data.get(benefits_field)
    household_income = session_data.get(household_income_field)

    if country not in (country_field_england, country_field_scotland, country_field_wales):
        return not_eligible

    if epc_rating in ("A", "B", "C") and accept_suggested_epc == field_yes:
        return not_eligible

    if own_property == own_property_field_social_housing:
        return eligible_for_gbis_and_eco4

    if park_home == field_yes and park_home_main_residence == field_no:
        return not_eligible

    if benefits == field_yes:
        return eligible_for_gbis_and_eco4

    if household_income == household_income_field_less_than_threshold:
        return eligible_for_gbis_and_eco4

    if park_home == field_yes:
        return eligible_for_gbis

    if _is_eligible_council_tax_band(country, council_tax_band):
        return eligible_for_gbis

    return not_eligible
