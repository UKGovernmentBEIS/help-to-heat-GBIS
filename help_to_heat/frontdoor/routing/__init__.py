from collections import deque

from help_to_heat.frontdoor.consts import govuk_start_page, unknown_page
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page

# in case of infinite loop ensure a route can't go on forever
# currently the longest route is under 30 pages
max_route_length = 100


def get_route(answers, target_page, start_page=None):
    if start_page is None:
        start_page = govuk_start_page

    route = deque([start_page])

    while len(route) < max_route_length:
        current_page = route[-1]

        if current_page == target_page:
            return route

        if current_page == unknown_page:
            raise CouldNotCalculateRouteException

        next_page = get_next_page(current_page, answers)

        route.append(next_page)

    raise CouldNotCalculateRouteException


class CouldNotCalculateRouteException(Exception):
    pass
