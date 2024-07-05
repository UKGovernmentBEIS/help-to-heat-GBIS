import logging
import uuid

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from marshmallow import ValidationError

from help_to_heat import portal, utils

from ..portal import email_handler
from . import eligibility, interface, schemas

SupplierConverter = interface.SupplierConverter

page_map = {}

logger = logging.getLogger(__name__)

page_compulsory_field_map = {
    "country": ("country",),
    "own-property": ("own_property",),
    "park-home": ("park_home",),
    "park-home-main-residence": ("park_home_main_residence",),
    "address": ("building_name_or_number", "postcode"),
    "epc-select": ("rrn",),
    "address-select": ("uprn",),
    "address-manual": ("address_line_1", "town_or_city", "postcode"),
    "council-tax-band": ("council_tax_band",),
    "epc": ("accept_suggested_epc",),
    "benefits": ("benefits",),
    "household-income": ("household_income",),
    "property-type": ("property_type",),
    "property-subtype": ("property_subtype",),
    "number-of-bedrooms": ("number_of_bedrooms",),
    "wall-type": ("wall_type",),
    "wall-insulation": ("wall_insulation",),
    "loft": ("loft",),
    "loft-access": ("loft_access",),
    "loft-insulation": ("loft_insulation",),
    "supplier": ("supplier",),
    "contact-details": ("first_name", "last_name"),
    "confirm-and-submit": ("permission", "acknowledge"),
}

missing_item_errors = {
    "country": _("Select where the property is located"),
    "own_property": _("Select if you own the property"),
    "park_home": _("Select if you live in a park home"),
    "park_home_main_residence": _("Select if the park home is your main residence"),
    "building_name_or_number": _("Enter building name or number"),
    "address_line_1": _("Enter Address line 1"),
    "postcode": _("Enter a postcode"),
    "uprn": _("Select your address"),
    "rrn": _("Select your address"),
    "town_or_city": _("Enter your Town or city"),
    "council_tax_band": _("Enter the Council Tax Band of the property"),
    "accept_suggested_epc": _("Select if your EPC rating is correct or not, or that you do not know"),
    "benefits": _("Select if anyone in your household is receiving any benefits listed below"),
    "household_income": _("Select your household income"),
    "property_type": _("Select your property type"),
    "property_subtype": _("Select your property type"),
    "number_of_bedrooms": _("Select the number of bedrooms the property has"),
    "wall_type": _("Select the type of walls the property has"),
    "wall_insulation": _("Select if the walls of the property are insulated or not, or if you do not know"),
    "loft": _("Select if you have a loft that has been converted into a room or not"),
    "loft_access": _("Select whether or not you have access to the loft"),
    "loft_insulation": _("Select whether or not your loft is fully insulated"),
    "supplier": _("Select your home energy supplier from the list below"),
    "first_name": _("Enter your first name"),
    "last_name": _("Enter your last name"),
    "email": _("Enter your email address"),
    "contact_number": _("Enter your contact number"),
    "permission": _("Please confirm that you agree to the use of your information by checking this box"),
    "acknowledge": _("Please confirm that you agree to the use of your information by checking this box"),
}

# to be updated when we get full list of excluded suppliers
converted_suppliers = ["Bulb, now part of Octopus Energy", "Utility Warehouse"]
unavailable_suppliers = []


def unavailable_supplier_redirect(session_id):
    session_data = interface.api.session.get_session(session_id)
    supplier = session_data["supplier"]
    if supplier not in unavailable_suppliers:
        return None

    if supplier in unavailable_suppliers:
        next_page_name = "applications-closed"
    return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)


def register_page(name):
    def _inner(func):
        page_map[name] = func
        return func

    return _inner


def redirect_to_homepage_view(request):
    next_url = "https://www.gov.uk/apply-great-british-insulation-scheme"
    return redirect(next_url)


def start_view(request):
    session_id = uuid.uuid4()
    next_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="country"))
    response = redirect(next_url)
    response["x-vcap-request-id"] = session_id
    return response


def holding_page_view(request):
    previous_path = "https://www.gov.uk/apply-great-british-insulation-scheme"
    context = {"previous_path": previous_path}
    return render(request, template_name="frontdoor/holding-page.html", context=context)


def sorry_page_view(request):
    return render(request, template_name="frontdoor/sorry-unavailable.html")


def not_found_page_view(request, exception):
    return render(request, template_name="frontdoor/not-found.html")


def page_view(request, session_id, page_name):
    if page_name not in (schemas.page_order + schemas.extra_pages + schemas.page_order_park_home):
        raise Http404("Invalid url")

    if page_name in page_map:
        return page_map[page_name](request, session_id, page_name)

    # Save a blank answer to record the page visit for analytics
    interface.api.session.save_answer(session_id, page_name, {"_page_name": page_name})
    prev_page_url, next_page_url = get_prev_next_urls(session_id, page_name)
    context = {"session_id": session_id, "page_name": page_name, "prev_url": prev_page_url}
    response = render(request, template_name=f"frontdoor/{page_name}.html", context=context)
    response["x-vcap-request-id"] = session_id
    return response


def change_page_view(request, session_id, page_name):
    assert page_name in page_map
    return page_map[page_name](request, session_id, page_name, is_change_page=True)


def get_prev_next_page_name(page_name, session_id=None):
    is_park_home = False
    is_social_housing = False
    receives_benefits = False

    if session_id:
        session_data = interface.api.session.get_session(session_id)
        is_park_home = session_data.get("park_home") == "Yes"
        is_social_housing = session_data.get("own_property") == "No, I am a social housing tenant"
        receives_benefits = session_data.get("benefits") == "Yes"

    # This question is asked first, so this path should take precedence in case users have
    # gone back and changed their answers
    if is_social_housing:
        mapping = schemas.page_prev_next_map_social_housing
        order = schemas.page_order_social_housing
    elif is_park_home:
        mapping = schemas.page_prev_next_map_park_home
        order = schemas.page_order_park_home
    else:
        mapping = schemas.page_prev_next_map
        order = schemas.page_order

    if page_name in mapping:
        prev_page_name = mapping[page_name]["prev"]
        next_page_name = mapping[page_name]["next"]
    else:
        assert page_name in order, page_name
        page_index = order.index(page_name)
        if page_index == 0:
            prev_page_name = "homepage"
        else:
            prev_page_name = order[page_index - 1]
        if page_index + 1 == len(order):
            next_page_name = None
        else:
            next_page_name = order[page_index + 1]

    if prev_page_name == "household-income" and receives_benefits:
        prev_page_name = "benefits"

    return prev_page_name, next_page_name


def get_prev_next_urls(session_id, page_name):
    prev_page_name, next_page_name = get_prev_next_page_name(page_name, session_id)
    if prev_page_name == "homepage":
        prev_page_url = "https://www.gov.uk/apply-great-british-insulation-scheme"
    else:
        prev_page_url = prev_page_name and reverse(
            "frontdoor:page", kwargs=dict(session_id=session_id, page_name=prev_page_name)
        )
    next_page_url = next_page_name and reverse(
        "frontdoor:page", kwargs=dict(session_id=session_id, page_name=next_page_name)
    )
    return prev_page_url, next_page_url


def reset_epc_details(session_id):
    interface.api.session.save_answer(
        session_id,
        "epc-select",
        {
            "rrn": "",
            "epc_details": {},
            "uprn": "",
            "property_main_heat_source": "",
            "epc_rating": "Not found",
            "accept_suggested_epc": "Not found",
            "epc_date": "",
        },
    )


class PageView(utils.MethodDispatcher):
    def get(self, request, session_id, page_name, data=None, errors=None, is_change_page=False):
        if not errors:
            errors = {}
        if not data:
            data = interface.api.session.get_answer(session_id, page_name)
        if is_change_page:
            assert page_name in schemas.change_page_lookup
            prev_page_name = schemas.change_page_lookup[page_name]
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=prev_page_name))
            next_page_url = None
        else:
            prev_page_url, next_page_url = self.get_prev_next_urls(session_id, page_name)

        session = interface.api.session.get_session(session_id)
        # Once a user has created a referral, they can no longer access their old session
        if "referral_created_at" in session and page_name != "success":
            return redirect("/")

        try:
            extra_context = self.get_context(request=request, session_id=session_id, page_name=page_name, data=data)
        except Exception:  # noqa:B902
            logger.exception("An unknown error occurred")
            return redirect("/sorry")
        context = {
            "data": data,
            "session_id": session_id,
            "page_name": page_name,
            "errors": errors,
            "prev_url": prev_page_url,
            "next_url": next_page_url,
            **extra_context,
        }

        response = render(request, template_name=f"frontdoor/{page_name}.html", context=context)
        response["x-vcap-request-id"] = session_id

        # Most pages will return previously entered data, which could be sensitive and thus should not be cached unless
        # explicitly okayed.
        if not ("safe_to_cache" in context and context["safe_to_cache"]):
            response["cache-control"] = "no-store"
            response["Pragma"] = "no-cache"
        return self.handle_get(response, request, session_id, page_name, context)

    def handle_get(self, response, request, session_id, page_name, context):
        return response

    def get_prev_next_urls(self, session_id, page_name):
        return get_prev_next_urls(session_id, page_name)

    def post(self, request, session_id, page_name, is_change_page=False):
        data = request.POST.dict()
        errors = self.validate(request, session_id, page_name, data, is_change_page)
        if errors:
            return self.get(request, session_id, page_name, data=data, errors=errors, is_change_page=is_change_page)
        else:
            try:
                data = self.save_data(request, session_id, page_name)
            except ValidationError as val_errors:
                errors = {field: val_errors.messages["data"][field][0] for field in val_errors.messages["data"]}
                return self.get(request, session_id, page_name, data=data, errors=errors, is_change_page=is_change_page)
            except Exception:  # noqa:B902
                logger.exception("An unknown error occurred saving data")
                return redirect("/sorry")
            return self.handle_post(request, session_id, page_name, data, is_change_page)

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = interface.api.session.save_answer(session_id, page_name, request.POST.dict())
        return data

    def get_context(self, request, session_id, page_name, data):
        return {}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        if is_change_page:
            assert page_name in schemas.change_page_lookup
            next_page_name = schemas.change_page_lookup[page_name]
        else:
            _, next_page_name = get_prev_next_page_name(page_name, session_id)
        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def validate(self, request, session_id, page_name, data, is_change_page):
        fields = page_compulsory_field_map.get(page_name, ())
        missing_fields = tuple(field for field in fields if not data.get(field))
        errors = {field: missing_item_errors[field] for field in missing_fields}
        return errors


@register_page("country")
class CountryView(PageView):
    def get_context(self, *args, **kwargs):
        return {"country_options": schemas.country_options_map}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        if data["country"] == "Northern Ireland":
            return redirect("frontdoor:page", session_id=session_id, page_name="northern-ireland")
        else:
            return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("own-property")
class OwnPropertyView(PageView):
    def get_context(self, *args, **kwargs):
        return {"own_property_options_map": schemas.own_property_options_map}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name, session_id)

        if is_change_page:
            assert page_name in schemas.change_page_lookup
            next_page_name = schemas.change_page_lookup[page_name]

        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def get_prev_next_urls(self, session_id, page_name):
        session_data = interface.api.session.get_session(session_id)
        request_supplier = session_data.get("supplier")
        prev_page_url, next_page_url = super().get_prev_next_urls(session_id, page_name)
        acquired_supplier_warning_pages = {
            "Bulb, now part of Octopus Energy": "bulb-warning-page",
            "Utility Warehouse": "utility-warehouse-warning-page",
            "Shell": "shell-warning-page",
        }
        if request_supplier in acquired_supplier_warning_pages:
            prev_page_url = reverse(
                "frontdoor:page",
                kwargs=dict(session_id=session_id, page_name=acquired_supplier_warning_pages[request_supplier]),
            )
        return prev_page_url, next_page_url


@register_page("park-home")
class ParkHomeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"park_home_options_map": schemas.park_home_options_map}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name, session_id)
        data = request.POST.dict()
        park_home = data.get("park_home")

        if park_home == "No":
            next_page_name = "address"

        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)


@register_page("park-home-main-residence")
class ParkHomeMainResidenceView(PageView):
    def get_context(self, *args, **kwargs):
        return {"park_home_main_residence_options_map": schemas.park_home_main_residence_options_map}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name, session_id)
        data = request.POST.dict()
        park_home_main_residence = data.get("park_home_main_residence")

        if is_change_page:
            assert page_name in schemas.change_page_lookup
            next_page_name = schemas.change_page_lookup[page_name]
        if park_home_main_residence == "No":
            next_page_name = "park-home-application-closed"

        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = request.POST.dict()
        park_home_main_residence = data.get("park_home_main_residence")
        if park_home_main_residence == "Yes":
            data["property_type"] = "Park home"
            data["property_subtype"] = "Park home"
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data


@register_page("address")
class AddressView(PageView):
    def handle_post(self, request, session_id, page_name, data, is_change_page):
        building_name_or_number = data["building_name_or_number"]
        postcode = data["postcode"]
        country = interface.api.session.get_answer(session_id, "country")["country"]
        reset_epc_details(session_id)
        try:
            if country == "Scotland":
                return redirect("frontdoor:page", session_id=session_id, page_name="address-select")
            else:
                address_and_rrn_details = interface.api.epc.get_address_and_epc_rrn(building_name_or_number, postcode)
                interface.api.session.save_answer(
                    session_id, page_name, {"address_and_rrn_details": address_and_rrn_details}
                )
                return redirect("frontdoor:page", session_id=session_id, page_name="epc-select")
        except Exception as e:  # noqa: B902
            logger.exception(f"An error occurred: {e}")
            return redirect("frontdoor:page", session_id=session_id, page_name="address-select")


@register_page("epc-select")
class EpcSelectView(PageView):
    def format_address(self, address):
        address_parts = [
            address["addressLine1"],
            address["addressLine2"],
            address["addressLine3"],
            address["addressLine4"],
            address["town"],
            address["postcode"],
        ]
        non_empty_address_parts = filter(None, address_parts)
        return ", ".join(non_empty_address_parts)

    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "address")
        address_and_rrn_details = data.get("address_and_rrn_details", "")
        rrn_options = tuple(
            {
                "value": a["epcRrn"],
                "label": self.format_address(a["address"]),
            }
            for a in address_and_rrn_details
        )
        return {"rrn_options": rrn_options}

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        rrn = request.POST["rrn"]

        try:
            epc = interface.api.epc.get_epc_details(rrn)
        except Exception as e:  # noqa: B902
            logger.exception(f"An error occurred: {e}")
            reset_epc_details(session_id)
            return redirect("frontdoor:page", session_id=session_id, page_name="address-select")

        address = self.format_address(epc["data"]["assessment"]["address"])
        epc_details = epc["data"]["assessment"]

        uprn = epc_details.get("uprn")
        heat_source = epc_details.get("mainHeatingDescription")

        epc_data = {
            "rrn": rrn,
            "address": address,
            "epc_details": epc_details,
            "uprn": uprn if uprn is not None else "",
            "property_main_heat_source": heat_source if heat_source is not None else "",
        }

        data = interface.api.session.save_answer(session_id, page_name, epc_data)
        return data


@register_page("address-select")
class AddressSelectView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "address")
        building_name_or_number = data["building_name_or_number"]
        postcode = data["postcode"]
        addresses = interface.api.address.find_addresses(building_name_or_number, postcode)
        uprn_options = tuple(
            {
                "value": a["uprn"],
                "label": f"""{a['address_line_1'] + ',' if a['address_line_1'] else ''}
                    {a['address_line_2'] + ',' if a['address_line_2'] else ''}
                    {a['town']}, {a['postcode']}""",
            }
            for a in addresses
        )
        return {"uprn_options": uprn_options}

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        uprn = request.POST["uprn"]
        data = interface.api.address.get_address(uprn)
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data


@register_page("address-manual")
class AddressManualView(PageView):
    def get_context(self, request, session_id, page_name, data, *args, **kwargs):
        answer_data = interface.api.session.get_answer(session_id, "address")
        data = {**answer_data, **data}
        return {"data": data}

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = request.POST.dict()
        fields = tuple(
            data.get(key) for key in ("address_line_1", "address_line_2", "town_or_city", "county", "postcode")
        )
        address = ", ".join(f for f in fields if f)
        data = {**data, "address": address}
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data

    def handle_post(self, request, session_id, page_name, data, is_change_page):  # noq E501
        reset_epc_details(session_id)
        return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("council-tax-band")
class CouncilTaxBandView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "country")
        selected_country = data.get("country")
        council_tax_bands = schemas.council_tax_band_options
        if selected_country == "Wales":
            council_tax_bands = schemas.welsh_council_tax_band_options
        return {"council_tax_band_options": council_tax_bands}


@register_page("epc")
class EpcView(PageView):
    def get_context(self, request, session_id, page_name, data):
        session_data = interface.api.session.get_session(session_id)
        country = session_data.get("country")

        if country == "Scotland":
            uprn = session_data.get("uprn")
            address = session_data.get("address")
            epc = interface.api.epc.get_epc_scotland(uprn) if uprn else {}

            context = {
                "epc_rating": epc.get("rating"),
                "epc_date": epc.get("date"),
                "epc_display_options": schemas.epc_display_options_map,
                "address": address,
            }

            return context
        else:
            rrn = session_data.get("rrn")
            address = session_data.get("address")
            context = {}
            epc = session_data.get("epc_details") if rrn else {}

            epc_band = epc.get("currentEnergyEfficiencyBand")

            context = {
                "epc_rating": epc_band.upper() if epc_band else "",
                "epc_date": epc.get("lodgementDate"),
                "epc_display_options": schemas.epc_display_options_map,
                "address": address,
            }
            return context

    def handle_get(self, response, request, session_id, page_name, context):
        session_data = interface.api.session.get_session(session_id)
        country = session_data.get("country")

        if country == "Scotland":
            uprn = session_data.get("uprn")
            epc = interface.api.epc.get_epc_scotland(uprn) if uprn else {}
        else:
            rrn = session_data.get("rrn")
            epc = session_data.get("epc_details") if rrn else {}

        if not epc:
            _, next_page_name = get_prev_next_page_name(page_name, session_id)
            return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)
        return super().handle_get(response, request, session_id, page_name, context)

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name, session_id)
        epc_rating = data.get("epc_rating").upper()
        accept_suggested_epc = data.get("accept_suggested_epc")

        if not epc_rating:
            return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

        if (epc_rating in ("A", "B", "C")) and (accept_suggested_epc == "Yes"):
            return redirect("frontdoor:page", session_id=session_id, page_name="epc-ineligible")

        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)


@register_page("benefits")
class BenefitsView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        context = interface.api.session.get_session(session_id)
        return {"benefits_options": schemas.yes_no_options_map, "context": context}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        benefits = data.get("benefits")
        session_data = interface.api.session.get_session(session_id)
        park_home = session_data.get("park_home")
        if benefits == "Yes":
            if park_home == "Yes":
                return redirect("frontdoor:page", session_id=session_id, page_name="summary")
            return redirect("frontdoor:page", session_id=session_id, page_name="property-type")
        return super().handle_post(request, session_id, page_name, data, is_change_page)

    def get_prev_next_urls(self, session_id, page_name):
        session_data = interface.api.session.get_session(session_id)
        park_home = session_data.get("park_home")
        epc_rating = session_data.get("epc_rating", "Not found")

        if park_home == "Yes" and epc_rating == "Not found":
            _, next_page_url = get_prev_next_urls(session_id, page_name)
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="address"))
            return prev_page_url, next_page_url
        else:
            return super().get_prev_next_urls(session_id, page_name)


@register_page("household-income")
class HouseholdIncomeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"household_income_options": schemas.household_income_options_map}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        # This is the final question that determines eligibility,
        # so we can check the eligible schemes to decide where to forward.
        session_data = interface.api.session.get_session(session_id)
        eligible_schemes = eligibility.calculate_eligibility(session_data)
        if len(eligible_schemes) == 0:
            return redirect("frontdoor:page", session_id=session_id, page_name="ineligible")
        else:
            return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("property-type")
class PropertyTypeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"property_type_options": schemas.property_type_options_map}

    def get_prev_next_urls(self, session_id, page_name):
        session_data = interface.api.session.get_session(session_id)
        own_property = session_data.get("own_property")
        epc_rating = session_data.get("epc_rating", "Not found")

        if own_property == "No, I am a social housing tenant" and epc_rating == "Not found":
            _, next_page_url = get_prev_next_urls(session_id, page_name)
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="address"))
            return prev_page_url, next_page_url
        else:
            return super().get_prev_next_urls(session_id, page_name)


@register_page("property-subtype")
class PropertySubtypeView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "property-type")
        property_type = data["property_type"]
        return {
            "property_type": schemas.property_subtype_titles_options_map[property_type],
            "property_subtype_options": schemas.property_subtype_options_map[property_type],
        }


@register_page("number-of-bedrooms")
class NumberOfBedroomsView(PageView):
    def get_context(self, *args, **kwargs):
        return {"number_of_bedrooms_options": schemas.number_of_bedrooms_options_map}


@register_page("wall-type")
class WallTypeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"wall_type_options": schemas.wall_type_options_map}


@register_page("wall-insulation")
class WallInsulationView(PageView):
    def get_context(self, *args, **kwargs):
        return {"wall_insulation_options": schemas.wall_insulation_options_map}


@register_page("loft")
class LoftView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_options": schemas.loft_options_map}

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = request.POST.dict()
        loft = data.get("loft")
        if loft == "No, I do not have a loft or my loft has been converted into a room":
            data["loft_access"] = "No loft"
            data["loft_insulation"] = "No loft"
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name)
        loft = data.get("loft")
        if loft == "No, I do not have a loft or my loft has been converted into a room":
            next_page_name = "summary"
        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)


@register_page("loft-access")
class LoftAccessView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_access_options": schemas.loft_access_options_map}


@register_page("loft-insulation")
class LoftInsulationView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_insulation_options": schemas.loft_insulation_options_map}

    def get_prev_next_urls(self, session_id, page_name):
        loft_data = interface.api.session.get_answer(session_id, "loft")

        if loft_data.get("loft", None) == "Yes, I have a loft that has not been converted into a room":
            _, next_page_url = get_prev_next_urls(session_id, page_name)
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="loft-access"))
            return prev_page_url, next_page_url
        else:
            return super().get_prev_next_urls(session_id, page_name)


@register_page("summary")
class SummaryView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        summary_lines = tuple(
            {
                "question": schemas.summary_map[question],
                "answer": self.get_answer(session_data, question),
                "change_url": self.get_change_url(session_id, question, page_name),
            }
            for page_name, questions in schemas.household_pages.items()
            for question in questions
            if self.show_question(session_data, question)
        )
        return {"summary_lines": summary_lines}

    def show_question(self, session_data, question):
        question_answered = question in session_data and question in schemas.summary_map
        if not question_answered:
            return False
        if question in ["property_type", "property_subtype"]:
            property_type = self.get_answer(session_data, "property_type")
            return property_type != "Park home"
        if question in ["park_home", "park_home_main_residence"]:
            own_property = self.get_answer(session_data, "own_property")
            return own_property != "No, I am a social housing tenant"
        if question == "epc_rating":
            epc_rating = session_data.get("epc_rating", "Not found")
            accept_suggested_epc = session_data.get("accept_suggested_epc")
            return epc_rating != "Not found" and accept_suggested_epc == "Yes"
        if question in ["loft_access", "loft_insulation"]:
            loft_answer = self.get_answer(session_data, "loft")
            return loft_answer == "Yes, I have a loft that has not been converted into a room"
        else:
            return True

    def get_answer(self, session_data, question):
        answer = session_data.get(question)
        answers_map = schemas.check_your_answers_options_map.get(question)
        return answers_map[answer] if answers_map else answer

    def get_change_url(self, session_id, question, page_name):
        if question == "park_home":
            return reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
        return reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=page_name))

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        supplier_redirect = unavailable_supplier_redirect(session_id)
        if supplier_redirect is not None:
            return supplier_redirect
        return super().handle_post(request, session_id, page_name, data, is_change_page)

    def get_prev_next_urls(self, session_id, page_name):
        session_data = interface.api.session.get_session(session_id)
        loft = session_data.get("loft")

        # if the user answered this, they went down the loft insulation route
        if loft == "Yes, I have a loft that has not been converted into a room":
            _, next_page_url = get_prev_next_urls(session_id, page_name)
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="loft-insulation"))
            return prev_page_url, next_page_url
        else:
            return super().get_prev_next_urls(session_id, page_name)


@register_page("schemes")
class SchemesView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        eligible_schemes = eligibility.calculate_eligibility(session_data)
        _ = interface.api.session.save_answer(session_id, "schemes", {"schemes": eligible_schemes})
        eligible_schemes = tuple(schemas.schemes_map[scheme] for scheme in eligible_schemes if not scheme == "ECO4")
        return {"eligible_schemes": eligible_schemes}


@register_page("supplier")
class SupplierView(PageView):
    def get_context(self, *args, **kwargs):
        return {"supplier_options": schemas.supplier_options}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name)
        request_data = dict(request.POST.dict())
        request_supplier = request_data.get("supplier")
        # to be updated when we get full list of excluded suppliers
        converted_suppliers = ["Bulb, now part of Octopus Energy", "Utility Warehouse", "Shell"]
        unavailable_suppliers = []
        if request_supplier == "Bulb, now part of Octopus Energy":
            next_page_name = "bulb-warning-page"
        if request_supplier == "Utility Warehouse":
            next_page_name = "utility-warehouse-warning-page"
        if request_supplier == "Shell":
            next_page_name = "shell-warning-page"
        if request_supplier in unavailable_suppliers:
            next_page_name = "applications-closed"

        if is_change_page:
            if (request_supplier in converted_suppliers) or (request_supplier in unavailable_suppliers):
                return redirect("frontdoor:change-page", session_id=session_id, page_name=next_page_name)
            else:
                assert page_name in schemas.change_page_lookup
                next_page_name = schemas.change_page_lookup[page_name]
        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = dict(request.POST.dict())
        request_supplier = data.get("supplier")
        data["user_selected_supplier"] = request_supplier
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data


@register_page("bulb-warning-page")
class BulbWarningPageView(PageView):
    pass


@register_page("utility-warehouse-warning-page")
class UtilityWarehousePageView(PageView):
    pass


@register_page("shell-warning-page")
class ShellWarningPageView(PageView):
    pass


@register_page("applications-closed")
class ApplicationsClosedView(PageView):
    def get_context(self, session_id, *args, **kwargs):
        supplier = SupplierConverter(session_id).get_supplier_on_general_pages()
        return {"supplier": supplier}


@register_page("contact-details")
class ContactDetailsView(PageView):
    def get_context(self, session_id, *args, **kwargs):
        supplier = SupplierConverter(session_id).get_supplier_on_general_pages()
        return {"supplier": supplier}

    def validate(self, request, session_id, page_name, data, is_change_page):
        fields = page_compulsory_field_map.get(page_name, ())
        missing_fields = tuple(field for field in fields if not data.get(field))
        errors = {field: missing_item_errors[field] for field in missing_fields}
        if (not data.get("email")) and (not data.get("contact_number")):
            errors = {
                **errors,
                "email": missing_item_errors["email"],
                "contact_number": missing_item_errors["contact_number"],
            }
        return errors


@register_page("confirm-and-submit")
class ConfirmSubmitView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        summary_lines = tuple(
            {
                "question": schemas.confirm_sumbit_map[question],
                "answer": session_data.get(question),
                "change_url": reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=page_name)),
            }
            for page_name, questions in schemas.details_pages.items()
            for question in questions
        )
        supplier = SupplierConverter(session_id).get_supplier_on_general_pages()
        return {"summary_lines": summary_lines, "supplier": supplier}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        supplier_redirect = unavailable_supplier_redirect(session_id)
        if supplier_redirect is not None:
            return supplier_redirect
        interface.api.session.create_referral(session_id)
        interface.api.session.save_answer(session_id, page_name, {"referral_created_at": str(timezone.now())})
        session_data = interface.api.session.get_session(session_id)
        session_data = SupplierConverter(session_id).replace_in_session_data(session_data)
        if session_data.get("email"):
            referral = portal.models.Referral.objects.get(session_id=session_id)
            session_data["referral_id"] = referral.formatted_referral_id
            email_handler.send_referral_confirmation_email(session_data, request.LANGUAGE_CODE)
        return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("success")
class SuccessView(PageView):
    def get_context(self, session_id, *args, **kwargs):
        supplier = SupplierConverter(session_id).get_supplier_on_success_page()
        referral = portal.models.Referral.objects.get(session_id=session_id)
        return {"supplier": supplier, "safe_to_cache": True, "referral_id": referral.formatted_referral_id}


class FeedbackView(utils.MethodDispatcher):
    def get(self, request, session_id=None, page_name=None, errors=None):
        template_name = "frontdoor/feedback.html"
        prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
        context = {
            "session_id": session_id,
            "page_name": page_name,
            "prev_url": prev_page_url,
            "multichoice_options_agreement": schemas.agreement_multichoice_options,
            "multichoice_options_satisfaction": schemas.satisfaction_multichoice_options,
            "multichoice_options_service_usage": schemas.service_usage_multichoice_options,
            "errors": errors,
        }
        return render(request, template_name=template_name, context=context)

    def post(self, request, session_id=None, page_name=None):
        data = request.POST.dict()
        errors = self.validate(data)
        if errors:
            return self.get(request, session_id, page_name, errors=errors)
        else:
            interface.api.feedback.save_feedback(session_id, page_name, data)
            if session_id and page_name:
                return redirect("frontdoor:feedback-thanks", session_id=session_id, page_name=page_name)

            else:
                return redirect("frontdoor:feedback-thanks")

    def validate(self, data):
        if (
            (not data.get("satisfaction"))
            and (not data.get("usage-reason"))
            and (not data.get("guidance"))
            and (not data.get("accuracy"))
            and (not data.get("advice"))
            and (data.get("more-detail") == "")
        ):
            errors = True
            return errors
        else:
            return None


def feedback_thanks_view(request, session_id=None, page_name=None):
    template_name = "frontdoor/feedback-thanks.html"
    prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
    context = {"session_id": session_id, "page_name": page_name, "prev_url": prev_page_url}
    return render(request, template_name=template_name, context=context)


def cookies_view(request):
    if request.method == "POST":
        consent = request.POST.get("cookies")
        previous_path = request.POST.get("prev")
        response = redirect(previous_path)
        response.set_cookie("cookiesAccepted", consent)
        return response
    else:
        return render(request, template_name="frontdoor/cookies.html")


def data_layer_js_view(request):
    # Remove after private beta (in favour of PC-275)
    return render(request, "dataLayer.js", {"gtag_id": settings.GTAG_ID}, content_type="application/x-javascript")


def privacy_policy_view(request, session_id=None, page_name=None):
    prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
    context = {
        "session_id": session_id,
        "page_name": page_name,
        "prev_url": prev_page_url,
    }
    return render(request, template_name="frontdoor/privacy-policy.html", context=context)


def accessibility_statement_view(request, session_id=None, page_name=None):
    prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
    context = {
        "session_id": session_id,
        "page_name": page_name,
        "prev_url": prev_page_url,
    }
    return render(request, template_name="frontdoor/accessibility-statement.html", context=context)


def error_page_view(request):
    raise Exception("could not serve page")
