from help_to_heat.frontdoor.consts import (
    country_page,
    govuk_start_page,
    unknown_page,
)
from help_to_heat.frontdoor.routing import (
    CouldNotCalculateRouteException,
    get_route,
)

start_page = country_page
# in case of infinite loop ensure a route can't go on forever
# currently the longest route is under 30 pages
max_route_length = 100


def get_prev_page(current_page, answers):
    # there is no previous page to this
    if current_page == govuk_start_page:
        return unknown_page

    try:
        route = get_route(answers, current_page)

        return route[-2]
    except CouldNotCalculateRouteException:
        return unknown_page
