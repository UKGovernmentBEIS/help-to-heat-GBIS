import datetime
import itertools
import unittest
import uuid

from help_to_heat.frontdoor import interface
from help_to_heat.frontdoor.eligibility import calculate_eligibility, country_council_tax_bands
from help_to_heat.frontdoor.mock_os_api import MockOSApi
from help_to_heat.portal import models

from . import utils


eligible_council_tax = {
    "England": {
        "eligible": ("A", "B", "C", "D"),
        "ineligible": ("E", "F", "G"),
    },
    # TODO Write Unit tests to properly test this logic
    # "Scotland": {
    #     "eligible": ("A", "B", "C", "D", "E"),
    #     "ineligible": ("F", "G"),
    # },
    "Wales": {
        "eligible": ("A", "B", "C", "D", "E"),
        "ineligible": ("F", "G"),
    },
}


def _add_epc(uprn, rating):
    models.EpcRating.objects.update_or_create(
        uprn=uprn, defaults={"rating": rating, "date": datetime.date(2022, 12, 25)}
    )
    assert interface.api.epc.get_epc(uprn, "England")


def _make_check_page(session_id):
    def _check_page(page, page_name, key, answer):
        form = page.get_form()
        form[key] = answer
        page = form.submit().follow()

        data = interface.api.session.get_answer(session_id, page_name=page_name)
        assert data[key] == answer
        return page

    return _check_page


@unittest.mock.patch("help_to_heat.frontdoor.interface.OSApi", MockOSApi)
@utils.mock_os_api
def test_ineligible_shortcut():
    for country in eligible_council_tax:
        for council_tax_band in eligible_council_tax[country]["ineligible"]:
            for epc_rating in ("D", "E", "F", "G"):
                _do_test(country=country, council_tax_band=council_tax_band, epc_rating=epc_rating)


def _do_test(country, council_tax_band, epc_rating):
    _add_epc(uprn="100023336956", rating=epc_rating)

    client = utils.get_client()
    page = client.get("/start")
    assert page.status_code == 302
    page = page.follow()

    assert page.status_code == 200
    session_id = page.path.split("/")[1]
    assert uuid.UUID(session_id)

    _check_page = _make_check_page(session_id)

    form = page.get_form()
    form["country"] = country
    page = form.submit().follow()

    assert page.has_one("h1:contains('Select your home energy supplier from the list below')")
    page = _check_page(page, "supplier", "supplier", "Utilita")

    assert page.has_text("Do you own the property?")
    page = _check_page(page, "own-property", "own_property", "Yes, I own my property and live in it")

    assert page.has_text("Do you live in a park home")
    page = _check_page(page, "park-home", "park_home", "No")

    form = page.get_form()
    form["building_name_or_number"] = "10"
    form["postcode"] = "SW1A 2AA"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address")
    assert data["building_name_or_number"] == "10"
    assert data["postcode"] == "SW1A 2AA"

    form = page.get_form()
    form["uprn"] = "100023336956"
    page = form.submit().follow()

    data = interface.api.session.get_answer(session_id, page_name="address-select")
    assert data["uprn"] == 100023336956
    assert data["address"] == "10, DOWNING STREET, LONDON, CITY OF WESTMINSTER, SW1A 2AA"

    assert page.has_one("h1:contains('What is the council tax band of your property?')")
    page = _check_page(page, "council-tax-band", "council_tax_band", council_tax_band)

    page = _check_page(page, "epc", "accept_suggested_epc", "Yes")

    page = _check_page(page, "benefits", "benefits", "No")

    assert page.has_one("h1:contains('Your property is not eligible')"), (country, council_tax_band, epc_rating)


# useful slices of tax codes
epc_ABC = ("A", "B", "C")
epc_DEFGU = ("D", "E", "F", "G", "Not found")
epc_FG = ("F", "G")
epc_DEU = ("D", "E", "Not found")
epcs = ("A", "B", "C", "D", "E", "F", "G")

yes = "Yes"
no = "No"
yes_no = (yes, no)
own_property_owner = "Yes, I own my property and live in it"
own_property_tenant = "No, I am a tenant"
own_property_landlord = "Yes, I am the property owner but I lease the property to one or more tenants"
own_property_social_housing = "No, I am a social housing tenant"
own_property_tenant_landlord = (own_property_tenant, own_property_landlord)
own_property_options = (own_property_owner, own_property_tenant, own_property_landlord, own_property_social_housing)
countries_england_scotland_wales = ("England", "Scotland", "Wales")
countries_not_england_scotland_wales = ("Northern Ireland",)
countries = countries_england_scotland_wales + countries_not_england_scotland_wales
council_tax_bands = ("A", "B", "C", "D", "E", "F", "G", "H", "I")
household_income_less_than_31k = "Less than £31,000 a year"
household_income_more_than_31k = "£31,000 or more a year"
household_incomes = (household_income_less_than_31k, household_income_more_than_31k)
property_type_park_home = "Park home"
property_types_not_park_home = ("House", "Bungalow", "Apartment, flat or maisonette")
property_types = property_types_not_park_home + (property_type_park_home,)

accept_both = ("GBIS", "ECO4")
accept_gbis = ("GBIS",)
deny = ()

count = 0

def _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating, benefits, household_income):
    global count
    count += 1
    print(count)
    return calculate_eligibility({
        "country": country,
        "property_type": property_type,
        "own_property": own_property,
        "park_home_main_residence": park_home_main_residence,
        "council_tax_band": council_tax_band,
        "epc_rating": epc_rating,
        "benefits": benefits,
        "household_income": household_income
    })


def test_scenario_1():
    for (country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_not_england_scotland_wales, own_property_options, property_types, yes_no, council_tax_bands, epcs, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_2():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = no

    for (country, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, council_tax_bands, epcs, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_3():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes

    for (country, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, council_tax_bands, epc_ABC, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_4():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = yes

    for (country, council_tax_band, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, council_tax_bands, epc_DEFGU, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both


def test_scenario_5():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = no
    household_income = household_income_less_than_31k

    for (country, council_tax_band, epc_rating) in itertools.product(countries_england_scotland_wales, council_tax_bands, epc_DEFGU):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both


def test_scenario_6():
    own_property = own_property_owner
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = no
    household_income = household_income_more_than_31k

    for (country, council_tax_band, epc_rating) in itertools.product(countries_england_scotland_wales, council_tax_bands, epc_DEFGU):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_gbis


def test_scenario_7():
    own_property = own_property_owner

    for (country, property_type, park_home_main_residence, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_ABC, yes_no, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_8():
    own_property = own_property_owner
    benefits = yes

    for (country, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_9():
    own_property = own_property_owner
    benefits = no
    household_income = household_income_less_than_31k

    for (country, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_10():
    own_property = own_property_owner
    benefits = no
    household_income = household_income_more_than_31k

    for (country, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_gbis


def test_scenario_11():
    own_property = own_property_owner

    for (country, property_type, park_home_main_residence, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_ABC, yes_no, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_12():
    own_property = own_property_owner
    benefits = no
    household_income = household_income_less_than_31k

    for (country, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_13():
    own_property = own_property_owner
    benefits = no
    household_income = household_income_more_than_31k

    for (country, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_14():
    own_property = own_property_owner
    benefits = yes

    for (country, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, property_types_not_park_home, yes_no, epc_DEFGU, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_15():
    property_type = property_type_park_home
    park_home_main_residence = no

    for (country, own_property, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epcs, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_16():
    property_type = property_type_park_home
    park_home_main_residence = yes

    for (country, own_property, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epc_ABC, yes_no, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_17():
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = yes

    for (country, own_property, council_tax_band, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epc_DEFGU, household_incomes):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both


def test_scenario_18():
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = no
    household_income = household_income_more_than_31k

    for (country, own_property, council_tax_band, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epc_DEFGU):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_gbis


def test_scenario_19():
    property_type = property_type_park_home
    park_home_main_residence = yes
    benefits = no
    household_income = household_income_less_than_31k

    for (country, own_property, council_tax_band, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, council_tax_bands, epc_DEFGU):
        assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both


def test_scenario_20():
    for (country, own_property, property_type, park_home_main_residence, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_ABC, yes_no, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_21():
    benefits = no
    household_income = household_income_more_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_FG):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_gbis


def test_scenario_22():
    benefits = yes

    for (country, own_property, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_FG, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_23():
    benefits = no
    household_income = household_income_less_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_FG):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_24():
    benefits = yes

    for (country, own_property, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEU, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_25():
    benefits = no
    household_income = household_income_less_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEU):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_26():
    benefits = no
    household_income = household_income_more_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEU):
        for council_tax_band in country_council_tax_bands[country]["eligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_gbis


def test_scenario_27():
    for (country, own_property, property_type, park_home_main_residence, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_ABC, yes_no, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_28():
    benefits = yes

    for (country, own_property, property_type, park_home_main_residence, epc_rating, household_income) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEFGU, household_incomes):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_29():
    benefits = no
    household_income = household_income_less_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == accept_both


def test_scenario_30():
    benefits = no
    household_income = household_income_more_than_31k

    for (country, own_property, property_type, park_home_main_residence, epc_rating) in itertools.product(countries_england_scotland_wales, own_property_tenant_landlord, property_types_not_park_home, yes_no, epc_DEFGU):
        for council_tax_band in country_council_tax_bands[country]["ineligible"]:
            assert _run_scenario(country, own_property, property_type, park_home_main_residence, council_tax_band, epc_rating,
                                 benefits, household_income) == deny


def test_scenario_31():
    for (country, property_type, park_home_main_residence, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, property_types, yes_no, council_tax_bands, epc_ABC, yes_no, household_incomes):
        assert _run_scenario(country, own_property_social_housing, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == deny


def test_scenario_32():
    for (country, property_type, park_home_main_residence, council_tax_band, epc_rating, benefits, household_income) in itertools.product(countries_england_scotland_wales, property_types, yes_no, council_tax_bands, epc_DEFGU, yes_no, household_incomes):
        assert _run_scenario(country, own_property_social_housing, property_type, park_home_main_residence, council_tax_band, epc_rating,
                             benefits, household_income) == accept_both
