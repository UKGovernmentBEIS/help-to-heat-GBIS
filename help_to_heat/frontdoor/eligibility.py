import functools
import logging

from . import schemas

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


def filter_scheme_names(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        result = func(*args, **kwargs)
        return tuple(schemas.schemes_map[scheme] for scheme in result)

    return _inner


@filter_scheme_names
def calculate_eligibility(session_data):
    """
    Calculate which schemes the user is able to use.  Based literally on the logic in the Mural file
    (hence why it is illogical)
    :param session_data:
    :return: A tuple of which schemes the person is eligible for, if any
    """
    epc_rating = session_data.get("epc_rating", "Not found")
    council_tax_band = session_data.get("council_tax_band")
    country = session_data.get("country")
    benefits = session_data.get("benefits")

    # Scenario 1
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["eligible"]:
            if epc_rating in ("E", "F", "G", "Not found"):
                if benefits in ("Yes",):
                    logger.error("Scenario 1")
                    return ("GBIS", "ECO4")

    # Scenario 2
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("E", "F", "G", "Not found"):
                if benefits in ("Yes",):
                    logger.error("Scenario 2")
                    return ("GBIS", "ECO4")

    # Scenario 3
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["eligible"]:
            if epc_rating in ("D", "E", "F", "G", "Not found"):
                if benefits in ("No",):
                    logger.error("Scenario 3a")
                    return ("GBIS",)

    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["eligible"]:
            if epc_rating in ("D", "Not Found"):
                if benefits in ("Yes",):
                    logger.error("Scenario 3b")
                    return ("GBIS",)

    # Scenario 3.1
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("D", "Not Found"):
                if benefits in ("Yes",):
                    logger.error("Scenario 3.1")
                    return ("GBIS",)

    # Scenario 4
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("D", "E", "F", "G"):
                if benefits in ("No",):
                    logger.error("Scenario 4")
                    return ()

    # Scenario 5
    if country in country_council_tax_bands:
        if council_tax_band in country_council_tax_bands[country]["ineligible"]:
            if epc_rating in ("Not found"):
                if benefits in ("No",):
                    logger.error("Scenario 5")
                    return ()

    return ()
