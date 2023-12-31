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

    # "Scenario 0"
    if property_type == "Park home":
        return ("GBIS",)

    # ECO4 and GBIS scenario 1 - home owner
    if country in country_council_tax_bands:
        if own_property in ("Yes, I own my property and live in it",):
            if epc_rating in ("D", "E", "F", "G", "Not found"):
                if benefits in ("Yes",):
                    return ("GBIS", "ECO4")

    # ECO4 and GBIS scenario 2 - private rented (tenant or landlord)
    if country in country_council_tax_bands:
        if own_property in (
            "No, I am a tenant",
            "Yes, I am the property owner but I lease the property to one or more tenants",
        ):
            if epc_rating in ("E", "F", "G", "Not found"):
                if benefits in ("Yes",):
                    return ("GBIS", "ECO4")

    # ECO4 and GBIS scenario 3 - social housing tenant
    if country in country_council_tax_bands:
        if own_property in ("No, I am a social housing tenant",):
            if epc_rating in ("D", "E", "F", "G", "Not found"):
                if benefits in ("Yes",):
                    return ("GBIS", "ECO4")

    # Scenario 3
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["eligible"]:
            if epc_rating in ("D", "E", "F", "G", "Not found"):
                if benefits in ("No",):
                    return ("GBIS",)

    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["eligible"]:
            if epc_rating in ("D", "Not Found"):
                if benefits in ("Yes",):
                    return ("GBIS",)

    # Scenario 3.1
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("D", "Not Found"):
                if benefits in ("Yes",):
                    return ("GBIS",)

    # Scenario 4
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("D", "E", "F", "G"):
                if benefits in ("No",):
                    return ()

    # Scenario 5
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("Not found"):
                if benefits in ("No",):
                    return ()

    return ()
