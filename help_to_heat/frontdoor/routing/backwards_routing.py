from collections import deque

from help_to_heat.frontdoor.consts import (
    country_page,
    govuk_start_page,
    unknown_page,
)
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page

start_page = country_page
# in case of infinite loop ensure a route can't go on forever
# currently the longest route is under 30 pages
max_route_length = 100


def get_prev_page(current_page, answers):
    route_page = start_page
    route = deque([govuk_start_page])

    while len(route) < max_route_length:
        if route_page == current_page:
            return route.pop()

        if route_page == unknown_page:
            return unknown_page

        next_page = get_next_page(route_page, answers)

        route.append(route_page)

        route_page = next_page

    return unknown_page
