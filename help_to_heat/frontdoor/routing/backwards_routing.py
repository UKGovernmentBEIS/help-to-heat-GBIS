from help_to_heat.frontdoor.consts import (
    country_page,
    govuk_start_page,
    unknown_page,
)
from help_to_heat.frontdoor.routing import calculate_journey

start_page = country_page
# in case of infinite loop ensure a journey can't go on forever
# currently the longest journey is under 30 pages
max_journey_length = 100


def get_prev_page(current_page, answers):
    # there is no previous page to this
    if current_page == govuk_start_page:
        return unknown_page

    journey = calculate_journey(answers, current_page)

    # if the page has been found, the last item in the list (index -1) will be the current page
    # so, the item before the last one (index -2) will be the previous page
    return journey[-2]
