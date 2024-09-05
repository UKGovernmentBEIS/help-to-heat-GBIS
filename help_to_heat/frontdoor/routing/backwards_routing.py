from collections import deque

from help_to_heat.frontdoor.consts import (
    country_page,
    govuk_start_page,
    unknown_page,
)
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page

start_page = country_page
# in case of infinite loop ensure a journey can't go on forever
# currently the longest journey is under 30 pages
max_journey_length = 100


def get_prev_page(current_page, answers):
    journey_page = start_page
    journey = deque([govuk_start_page])

    while len(journey) < max_journey_length:
        if journey_page == current_page:
            return journey.pop()

        if journey_page == unknown_page:
            return unknown_page

        next_page = get_next_page(journey_page, answers)

        journey.append(journey_page)

        journey_page = next_page

    return unknown_page
