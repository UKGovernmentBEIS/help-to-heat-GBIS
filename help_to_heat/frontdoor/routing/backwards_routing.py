from help_to_heat.frontdoor.consts import (
    country_page,
    govuk_start_page,
    unknown_page,
)
from help_to_heat.frontdoor.routing.forwards_routing import get_next_page

start_page = country_page
max_route_length = 100


def get_prev_page(current_page, answers):
    route_page = start_page
    route = [govuk_start_page]

    while len(route) < max_route_length:
        if route_page == current_page:
            return route[-1]

        if route_page == unknown_page:
            return unknown_page

        next_page, redirect = get_next_page(route_page, answers)

        if not redirect:
            route.append(route_page)

        route_page = next_page

    return unknown_page
