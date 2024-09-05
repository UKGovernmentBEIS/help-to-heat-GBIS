from collections import deque

from help_to_heat.frontdoor.consts import govuk_start_page, unknown_page
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page

# in case of infinite loop ensure a journey can't go on forever
# currently the longest journey is under 30 pages
max_journey_length = 100


def calculate_journey(answers, to_page, from_page=None):
    """
    Calculates the journey through the site the user will take given their current answers, stopping at the specified
    page.

    Parameters
    ----------
    answers
        All answers given by the user so far
    to_page
        The page the journey should be calculated to
    from_page
        The page the journey should be calculated from. If not given journey will be calculated from govuk_start_page

    Returns
    -------
    List[str]
        List of pages between from_page and to_page, inclusive at both ends

    """
    if from_page is None:
        from_page = govuk_start_page

    journey = deque([from_page])

    while len(journey) < max_journey_length:
        current_page = journey[-1]

        if current_page == to_page:
            return list(journey)

        if current_page == unknown_page:
            raise CouldNotCalculateJourneyException

        next_page = get_next_page(current_page, answers)

        journey.append(next_page)

    raise CouldNotCalculateJourneyException


class CouldNotCalculateJourneyException(Exception):
    pass
