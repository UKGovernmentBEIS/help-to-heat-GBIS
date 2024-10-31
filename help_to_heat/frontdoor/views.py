import logging
import uuid
from datetime import datetime

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
from .consts import (
    address_all_address_and_lmk_details_field,
    address_building_name_or_number_field,
    address_choice_field,
    address_choice_field_enter_manually,
    address_choice_field_epc_api_fail,
    address_choice_field_write_address,
    address_field,
    address_manual_address_line_1_field,
    address_manual_address_line_2_field,
    address_manual_county_field,
    address_manual_page,
    address_manual_postcode_field,
    address_manual_town_or_city_field,
    address_page,
    address_postcode_field,
    address_select_choice_field,
    address_select_choice_field_enter_manually,
    address_select_choice_field_select_address,
    address_select_manual_page,
    address_select_page,
    all_pages,
    benefits_field,
    benefits_page,
    bulb_warning_page,
    bulb_warning_page_field,
    confirm_and_submit_acknowledge_field,
    confirm_and_submit_page,
    confirm_and_submit_permission_field,
    contact_details_contact_number_field,
    contact_details_email_field,
    contact_details_first_name_field,
    contact_details_last_name_field,
    contact_details_page,
    council_tax_band_field,
    council_tax_band_page,
    country_field,
    country_field_england,
    country_field_scotland,
    country_field_wales,
    country_page,
    duplicate_uprn_field,
    epc_accept_suggested_epc_field,
    epc_accept_suggested_epc_field_not_found,
    epc_details_field,
    epc_found_field,
    epc_ineligible_page,
    epc_page,
    epc_rating_field,
    epc_rating_field_not_found,
    epc_rating_is_eligible_field,
    epc_select_choice_field,
    epc_select_choice_field_enter_manually,
    epc_select_choice_field_epc_api_fail,
    epc_select_choice_field_select_epc,
    epc_select_manual_page,
    epc_select_page,
    field_no,
    field_yes,
    govuk_start_page,
    govuk_start_page_url,
    household_income_field,
    household_income_field_more_than_threshold,
    household_income_page,
    lmk_field,
    lmk_field_enter_manually,
    loft_access_field,
    loft_access_field_yes,
    loft_access_page,
    loft_field,
    loft_field_yes,
    loft_insulation_field,
    loft_insulation_field_dont_know,
    loft_insulation_field_less_than_threshold,
    loft_insulation_field_more_than_threshold,
    loft_insulation_page,
    loft_page,
    no_epc_field,
    no_epc_page,
    northern_ireland_ineligible_page,
    number_of_bedrooms_field,
    number_of_bedrooms_page,
    own_property_field,
    own_property_field_social_housing,
    own_property_page,
    page_name_field,
    park_home_field,
    park_home_ineligible_page,
    park_home_main_residence_field,
    park_home_main_residence_page,
    park_home_page,
    property_ineligible_page,
    property_subtype_field,
    property_subtype_page,
    property_type_field,
    property_type_page,
    recommendations_field,
    referral_already_submitted_field,
    referral_already_submitted_page,
    schemes_contribution_acknowledgement_field,
    schemes_field,
    schemes_page,
    schemes_ventilation_acknowledgement_field,
    shell_warning_page,
    shell_warning_page_field,
    success_page,
    summary_page,
    supplier_field,
    supplier_page,
    unknown_page,
    uprn_field,
    uprn_field_enter_manually,
    user_selected_supplier_field,
    utility_warehouse_warning_page,
    utility_warehouse_warning_page_field,
    wall_insulation_field,
    wall_insulation_field_dont_know,
    wall_insulation_field_no,
    wall_insulation_field_some,
    wall_insulation_page,
    wall_type_field,
    wall_type_field_cavity,
    wall_type_field_dont_know,
    wall_type_field_mix,
    wall_type_field_solid,
    wall_type_page,
)
from .eligibility import calculate_eligibility, eco4
from .routing import CouldNotCalculateJourneyException, calculate_journey
from .routing.backwards_routing import get_prev_page
from .routing.forwards_routing import get_next_page
from .session_handlers.duplicate_referral_checker import (
    DuplicateReferralChecker,
)

SupplierConverter = interface.SupplierConverter

page_map = {}

logger = logging.getLogger(__name__)

page_compulsory_field_map = {
    country_page: (country_field,),
    own_property_page: (own_property_field,),
    park_home_page: (park_home_field,),
    park_home_main_residence_page: (park_home_main_residence_field,),
    address_page: (address_building_name_or_number_field, address_postcode_field),
    epc_select_page: (lmk_field,),
    address_select_page: (uprn_field,),
    address_manual_page: (
        address_manual_address_line_1_field,
        address_manual_town_or_city_field,
        address_manual_postcode_field,
    ),
    epc_select_manual_page: (
        address_manual_address_line_1_field,
        address_manual_town_or_city_field,
        address_manual_postcode_field,
    ),
    address_select_manual_page: (
        address_manual_address_line_1_field,
        address_manual_town_or_city_field,
        address_manual_postcode_field,
    ),
    referral_already_submitted_page: (referral_already_submitted_field,),
    council_tax_band_page: (council_tax_band_field,),
    epc_page: (epc_accept_suggested_epc_field,),
    benefits_page: (benefits_field,),
    household_income_page: (household_income_field,),
    property_type_page: (property_type_field,),
    property_subtype_page: (property_subtype_field,),
    number_of_bedrooms_page: (number_of_bedrooms_field,),
    wall_type_page: (wall_type_field,),
    wall_insulation_page: (wall_insulation_field,),
    loft_page: (loft_field,),
    loft_access_page: (loft_access_field,),
    loft_insulation_page: (loft_insulation_field,),
    supplier_page: (supplier_field,),
    contact_details_page: (contact_details_first_name_field, contact_details_last_name_field),
    confirm_and_submit_page: (confirm_and_submit_permission_field, confirm_and_submit_acknowledge_field),
}

missing_item_errors = {
    country_field: _("Select where the property is located"),
    own_property_field: _("Select if you own the property"),
    park_home_field: _("Select if you live in a park home"),
    park_home_main_residence_field: _("Select if the park home is your main residence"),
    address_building_name_or_number_field: _("Enter building name or number"),
    address_manual_address_line_1_field: _("Enter Address line 1"),
    address_postcode_field: _("Enter a postcode"),
    uprn_field: _("Select your address, or I can't find my address if your address is not listed"),
    lmk_field: _("Select your address, or I can't find my address if your address is not listed"),
    address_manual_town_or_city_field: _("Enter your Town or city"),
    referral_already_submitted_field: _("Please confirm that you want to submit another referral"),
    council_tax_band_field: _("Enter the Council Tax Band of the property"),
    epc_accept_suggested_epc_field: _("Select if your EPC rating is correct or not, or that you do not know"),
    benefits_field: _("Select if anyone in your household is receiving any benefits listed below"),
    household_income_field: _("Select your household income"),
    property_type_field: _("Select your property type"),
    property_subtype_field: _("Select your property type"),
    number_of_bedrooms_field: _("Select the number of bedrooms the property has"),
    wall_type_field: _("Select the type of walls the property has"),
    wall_insulation_field: _("Select if the walls of the property are insulated or not, or if you do not know"),
    loft_field: _("Select if you have a loft that has been converted into a room or not"),
    loft_access_field: _("Select whether or not you have access to the loft"),
    loft_insulation_field: _("Select whether or not your loft is fully insulated"),
    supplier_field: _("Select your home energy supplier from the list below"),
    contact_details_first_name_field: _("Enter your first name"),
    contact_details_last_name_field: _("Enter your last name"),
    contact_details_email_field: _("Enter your email address"),
    contact_details_contact_number_field: _("Enter your contact number"),
    confirm_and_submit_permission_field: _(
        "Please confirm that you agree to the use of your information by checking this box"
    ),
    confirm_and_submit_acknowledge_field: _(
        "Please confirm that you agree to the use of your information by checking this box"
    ),
    schemes_ventilation_acknowledgement_field: _(
        "Please confirm that you understand your home must be sufficiently ventilated before any insulation is "
        "installed"
    ),
    schemes_contribution_acknowledgement_field: _(
        "Please confirm that you understand you may be required to contribute towards the cost of installing insulation"
    ),
}

month_names = [
    _("January"),
    _("February"),
    _("March"),
    _("April"),
    _("May"),
    _("June"),
    _("July"),
    _("August"),
    _("September"),
    _("October"),
    _("November"),
    _("December"),
]

# to be updated when we get full list of excluded suppliers
converted_suppliers = ["Bulb, now part of Octopus Energy", "Utility Warehouse"]
unavailable_suppliers = []


def unavailable_supplier_redirect(session_id):
    session_data = interface.api.session.get_session(session_id)
    supplier = session_data[supplier_field]
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
    next_url = govuk_start_page_url
    return redirect(next_url)


def start_view(request):
    session_id = uuid.uuid4()
    next_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="country"))
    response = redirect(next_url)
    response["x-vcap-request-id"] = session_id
    return response


def holding_page_view(request):
    previous_path = govuk_start_page_url
    context = {"previous_path": previous_path, "govuk_url": govuk_start_page_url}
    return render(request, template_name="frontdoor/holding-page.html", context=context)


def sorry_page_view(request):
    return render(request, template_name="frontdoor/sorry-unavailable.html")


def sorry_journey_page_view(request):
    return render(request, template_name="frontdoor/sorry-journey.html")


def not_found_page_view(request, exception):
    return render(request, template_name="frontdoor/not-found.html")


def page_view(request, session_id, page_name):
    if page_name not in all_pages:
        raise Http404("Invalid url")

    if page_name in page_map:
        return page_map[page_name](request, session_id, page_name)

    # Save a blank answer to record the page visit for analytics
    save_answer(session_id, page_name, {"_page_name": page_name})
    answers = interface.api.session.get_session(session_id)
    prev_page_url = get_prev_page(page_name, answers)
    context = {"session_id": session_id, "page_name": page_name, "prev_url": prev_page_url}
    response = render(request, template_name=f"frontdoor/{page_name}.html", context=context)
    response["x-vcap-request-id"] = session_id
    return response


def change_page_view(request, session_id, page_name):
    assert page_name in page_map
    return page_map[page_name](request, session_id, page_name, is_change_page=True)


def page_name_to_url(session_id, page_name, is_change_page=False):
    if page_name == unknown_page:
        return reverse("frontdoor:sorry-unavailable")
    if page_name == govuk_start_page:
        return govuk_start_page_url
    return reverse(
        "frontdoor:page" if not is_change_page else "frontdoor:change-page",
        kwargs=dict(session_id=session_id, page_name=page_name),
    )


def save_answer(session_id, page_name, answer):
    return interface.api.session.save_answer(session_id, page_name, answer)


def reset_epc_details(session_id):
    save_answer(
        session_id,
        "epc-select",
        {
            lmk_field: "",
            epc_details_field: {},
            uprn_field: "",
            epc_rating_field: epc_rating_field_not_found,
            epc_accept_suggested_epc_field: epc_accept_suggested_epc_field_not_found,
            "epc_date": "",
        },
    )


class PageView(utils.MethodDispatcher):
    def get(self, request, session_id, page_name, unsaved_data=None, errors=None, is_change_page=False):
        if not errors:
            errors = {}
        answers = interface.api.session.get_session(session_id)
        data = interface.api.session.get_answer(session_id, page_name)

        # if there were validation errors some user inputted data won't have been stored as an answer
        # they will be passed as unsaved_data so that they don't disappear from the page
        if unsaved_data:
            data = {**data, **unsaved_data}

        data_with_get_answers = self.save_get_data(data.copy(), session_id, page_name)
        # only save an answer on get if new answers were given
        if data_with_get_answers != data:
            save_answer(session_id, page_name, data_with_get_answers)

        if page_name not in schemas.routing_overrides:
            try:
                # ensure the user has answers to complete the journey to this page
                calculate_journey(answers, to_page=page_name)
            except CouldNotCalculateJourneyException as e:
                logger.exception(e)
                return redirect("/sorry-journey")

        prev_page_url = self._get_prev_page_url(request, session_id, page_name, is_change_page)

        # Once a user has created a referral, they can no longer access their old session
        if "referral_created_at" in answers and page_name != "success":
            return redirect("/")

        extra_context = self.build_extra_context(
            request=request,
            session_id=session_id,
            page_name=page_name,
            data=data_with_get_answers,
            is_change_page=is_change_page,
        )

        context = {
            "data": data_with_get_answers,
            "session_id": session_id,
            "page_name": page_name,
            "errors": errors,
            "prev_url": prev_page_url,
            **extra_context,
        }

        response = render(request, template_name=f"frontdoor/{page_name}.html", context=context)
        response["x-vcap-request-id"] = session_id

        # Most pages will return previously entered data, which could be sensitive and thus should not be cached unless
        # explicitly okayed.
        if not ("safe_to_cache" in context and context["safe_to_cache"]):
            response["cache-control"] = "no-store"
            response["Pragma"] = "no-cache"
        return response

    def post(self, request, session_id, page_name, is_change_page=False):
        data = request.POST.dict()
        errors = self.validate(request, session_id, page_name, data, is_change_page)
        if errors:
            return self.get(
                request, session_id, page_name, unsaved_data=data, errors=errors, is_change_page=is_change_page
            )
        else:
            try:
                data_with_post_answers = self.save_post_data(data.copy(), session_id, page_name)
                save_answer(session_id, page_name, data_with_post_answers)
            except ValidationError as val_errors:
                errors = {field: val_errors.messages["data"][field][0] for field in val_errors.messages["data"]}
                return self.get(
                    request, session_id, page_name, unsaved_data=data, errors=errors, is_change_page=is_change_page
                )
            except Exception:  # noqa:B902
                logger.exception("An unknown error occurred saving data")
                return redirect("/sorry")

            answers = interface.api.session.get_session(session_id)
            self.handle_saved_answers(request, session_id, page_name, answers, is_change_page)

            next_page_name = get_next_page(page_name, answers)

            if is_change_page:
                if next_page_name in schemas.change_page_override_pages:
                    return redirect("frontdoor:change-page", session_id=session_id, page_name=next_page_name)

                assert page_name in schemas.change_page_lookup
                change_page = schemas.change_page_lookup[page_name]
                start_of_journey = schemas.change_page_start_of_journey_lookup[change_page]

                try:
                    # ensure the user has answers to complete the journey
                    calculate_journey(answers, from_page=start_of_journey, to_page=change_page)
                    return redirect("frontdoor:page", session_id=session_id, page_name=change_page)
                except CouldNotCalculateJourneyException as e:
                    # if not, take them to the question that is preventing them from finishing
                    # for instance, if the journey ends at the park home main resident page (and not summary page), then
                    # this must mean the user hasn't given an answer to it
                    # so, extract the last page in the route and send the user there in the change page state
                    # this cycle keeps happening until a journey to summary can be completed, at which point we know
                    # the user has now answered all required questions
                    last_page_name = e.partial_journey[-1]
                    return redirect("frontdoor:change-page", session_id=session_id, page_name=last_page_name)

            if next_page_name == unknown_page:
                return redirect("/sorry")
            return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        """
        Build any additional data to be added to the context.

        This will be available to use in the template html file.
        """
        return {}

    def save_get_data(self, data, session_id, page_name):
        """
        Add any additional answers to be saved on GET

        Should be using sparingly and not for routing purposes, else user could be rerouted on pressing refresh

        For instance, saving tracking data when a user loads the page

        data will be the user submitted data for this page
        """
        return data

    def save_post_data(self, data, session_id, page_name):
        """
        Add any additional answers to be saved to the session on POST

        For instance, checking and storing whether the UPRN is duplicate

        data will be the user submitted data for this page

        The returned data object will be used to decide which page to send to
        """
        return data

    def handle_saved_answers(self, request, session_id, page_name, answers, is_change_page):
        """
        Any additional logic to run post the answers being saved to the session. Redirects are not possible here.
        Use routing methods to implement changes to the flow

        For instance, sending emails on submit
        """
        pass

    def validate(self, request, session_id, page_name, data, is_change_page):
        fields = page_compulsory_field_map.get(page_name, ())
        missing_fields = tuple(field for field in fields if not data.get(field))
        errors = {field: missing_item_errors[field] for field in missing_fields}
        return errors

    def _get_prev_page_url(self, request, session_id, page_name, is_change_page):
        answers = interface.api.session.get_session(session_id)

        if is_change_page:
            # for pages that block progression, allow the user to press back out of these whilst keeping change state
            if page_name in schemas.change_page_override_pages:
                prev_page_name = get_prev_page(page_name, answers)
                return reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=prev_page_name))
            else:
                assert page_name in schemas.change_page_lookup
                change_page_name = schemas.change_page_lookup[page_name]
                start_of_journey_page = schemas.change_page_start_of_journey_lookup[change_page_name]

                try:
                    # it is possible the user has changed answers that mean they no longer complete the flow
                    # check whether their answers can lead to the summary page
                    calculate_journey(answers, from_page=start_of_journey_page, to_page=change_page_name)
                    prev_page_name = schemas.change_page_lookup[page_name]
                    return reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=prev_page_name))
                except CouldNotCalculateJourneyException:
                    # if not, as a failsafe send them to the previous page in change state
                    # this is a reasonably unsurprising action to the user, it is the previous page
                    # TODO PC-1311: review further
                    prev_page_name = get_prev_page(page_name, answers)
                    return reverse(
                        "frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=prev_page_name)
                    )

        if page_name in schemas.routing_overrides:
            return page_name_to_url(session_id, schemas.routing_overrides[page_name]["prev_page"])

        return page_name_to_url(session_id, get_prev_page(page_name, answers))


@register_page(country_page)
class CountryView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"country_options": schemas.country_options_map}


@register_page(supplier_page)
class SupplierView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"supplier_options": schemas.supplier_options}

    def save_post_data(self, data, session_id, page_name):
        request_supplier = data.get(supplier_field)
        data[user_selected_supplier_field] = request_supplier
        return data


@register_page(own_property_page)
class OwnPropertyView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"own_property_options_map": schemas.own_property_options_map}


@register_page(park_home_page)
class ParkHomeView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"park_home_options_map": schemas.park_home_options_map}


@register_page(park_home_main_residence_page)
class ParkHomeMainResidenceView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"park_home_main_residence_options_map": schemas.park_home_main_residence_options_map}


@register_page(address_page)
class AddressView(PageView):
    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        return {"manual_url": page_name_to_url(session_id, address_manual_page, is_change_page)}

    def save_post_data(self, data, session_id, page_name):
        reset_epc_details(session_id)
        country = data.get(country_field)
        building_name_or_number = data.get(address_building_name_or_number_field)
        postcode = data.get(address_postcode_field)
        try:
            data[address_choice_field] = address_choice_field_write_address
            if country != country_field_scotland:
                address_and_lmk_details = interface.api.epc.get_address_and_epc_lmk(building_name_or_number, postcode)
                data[address_all_address_and_lmk_details_field] = address_and_lmk_details
        except Exception as e:  # noqa: B902
            logger.exception(f"An error occurred: {e}")
            data[address_choice_field] = address_choice_field_epc_api_fail

        return data


@register_page(epc_select_page)
class EpcSelectView(PageView):
    def format_address(self, address):
        address_parts = [
            address["address1"],
            address["address2"],
            address["address3"],
            address["posttown"],
            address["postcode"],
        ]
        non_empty_address_parts = filter(None, address_parts)
        return ", ".join(non_empty_address_parts)

    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        data = interface.api.session.get_answer(session_id, address_page)
        address_and_rrn_details = data.get(address_all_address_and_lmk_details_field, [])
        lmk_options = tuple(
            {
                "value": a["lmk-key"],
                "label": self.format_address(a),
            }
            for a in address_and_rrn_details
        )

        fallback_option = (
            {"value": lmk_field_enter_manually, "label": _("I cannot find my address, I want to enter it manually")}
            if len(lmk_options) > 0
            else None
        )

        return {
            "lmk_options": lmk_options,
            "manual_url": page_name_to_url(session_id, epc_select_manual_page, is_change_page),
            "fallback_option": fallback_option,
        }

    def save_post_data(self, data, session_id, page_name):
        lmk = data.get(lmk_field)

        if lmk == lmk_field_enter_manually:
            data[epc_select_choice_field] = epc_select_choice_field_enter_manually
            return data

        try:
            epc_details_response, epc_recommendations_response = interface.api.epc.get_epc(lmk)
            epc_details = epc_details_response["rows"][0]
            recommendations = epc_recommendations_response["rows"]
        except Exception as e:  # noqa: B902
            logger.exception(f"An error occurred: {e}")
            reset_epc_details(session_id)
            data[epc_select_choice_field] = epc_select_choice_field_epc_api_fail
            return data

        data[epc_select_choice_field] = epc_select_choice_field_select_epc

        uprn = epc_details.get("uprn")
        address = epc_details.get("address")

        epc_data = {
            lmk_field: lmk,
            address_field: address,
            epc_details_field: epc_details,
            recommendations_field: recommendations,
            uprn_field: uprn if uprn is not None else "",
        }

        data = {**data, **epc_data}

        duplicate_referral_checker = DuplicateReferralChecker(session_id, data)
        data[duplicate_uprn_field] = (
            field_yes if duplicate_referral_checker.is_referral_a_recent_duplicate() else field_no
        )
        data[epc_found_field] = field_yes
        return data


@register_page(address_select_page)
class AddressSelectView(PageView):
    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        data = interface.api.session.get_answer(session_id, address_page)
        building_name_or_number = data[address_building_name_or_number_field]
        postcode = data[address_postcode_field]
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

        fallback_option = (
            {"value": uprn_field_enter_manually, "label": _("I cannot find my address, I want to enter it manually")}
            if len(uprn_options) > 0
            else None
        )

        return {
            "uprn_options": uprn_options,
            "manual_url": page_name_to_url(session_id, address_select_manual_page, is_change_page),
            "fallback_option": fallback_option,
        }

    def save_post_data(self, data, session_id, page_name):
        uprn = data.get(uprn_field)

        if uprn == uprn_field_enter_manually:
            data[address_select_choice_field] = address_select_choice_field_enter_manually
            return data

        data[address_select_choice_field] = address_select_choice_field_select_address

        address_data = interface.api.address.get_address(uprn)
        data[address_field] = address_data["address"]

        duplicate_referral_checker = DuplicateReferralChecker(session_id)
        data[duplicate_uprn_field] = (
            field_yes if duplicate_referral_checker.is_referral_a_recent_duplicate() else field_no
        )

        answers = interface.api.session.get_session(session_id)
        country = answers.get(country_field)

        data[epc_found_field] = field_no

        if country == country_field_scotland and uprn is not None:
            epc = interface.api.epc.get_epc_scotland(uprn)
            if epc != {}:
                epc_details = {"current-energy-rating": epc.get("rating"), "lodgement-date": epc.get("date")}
                data[epc_details_field] = epc_details
                data[epc_found_field] = field_yes

        return data


@register_page(referral_already_submitted_page)
class ReferralAlreadySubmitted(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        duplicate_referral_checker = DuplicateReferralChecker(session_id)
        to_same_energy_supplier = duplicate_referral_checker.is_recent_duplicate_referral_sent_to_same_energy_supplier()
        date_created = duplicate_referral_checker.get_date_of_previous_referral().strftime("%d/%m/%Y")
        address = session_data.get(address_field)
        supplier = session_data.get(supplier_field)
        return {
            "to_same_energy_supplier": to_same_energy_supplier,
            "date_created": date_created,
            "address": address,
            "supplier": supplier,
        }


# so that the routing can discern which way to go, there are three registered manual pages
# these use the same template and share a view
# the user is linked here directly, bypassing the routing logic. this means back button url must be manually given
# after submitting, an answer that the user went this way is saved to the session. normal routing can take over again
@register_page(address_manual_page)
@register_page(epc_select_manual_page)
@register_page(address_select_manual_page)
class AddressManualView(PageView):
    def build_extra_context(self, request, session_id, page_name, data, *args, **kwargs):
        answer_data = interface.api.session.get_answer(session_id, address_page)
        data = {**answer_data, **data}

        return {"data": data}

    def save_post_data(self, data, session_id, page_name):
        reset_epc_details(session_id)
        fields = tuple(
            data.get(key)
            for key in (
                address_manual_address_line_1_field,
                address_manual_address_line_2_field,
                address_manual_town_or_city_field,
                address_manual_county_field,
                address_manual_postcode_field,
            )
        )
        address = ", ".join(f for f in fields if f)
        data[address_field] = address
        data[duplicate_uprn_field] = field_no
        data[epc_found_field] = field_no

        if page_name == address_manual_page:
            data[address_choice_field] = address_choice_field_enter_manually
        if page_name == epc_select_manual_page:
            data[epc_select_choice_field] = epc_select_choice_field_enter_manually
        if page_name == address_select_manual_page:
            data[address_select_choice_field] = address_select_choice_field_enter_manually

        return data


@register_page(council_tax_band_page)
class CouncilTaxBandView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, country_page)
        selected_country = data.get(country_field)
        council_tax_bands = schemas.council_tax_band_options
        if selected_country == country_field_wales:
            council_tax_bands = schemas.welsh_council_tax_band_options
        return {"council_tax_band_options": council_tax_bands}


@register_page(epc_page)
class EpcView(PageView):
    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        session_data = interface.api.session.get_session(session_id)

        address = session_data.get(address_field)
        show_monthly_epc_update_details = session_data.get(country_field) in [
            country_field_wales,
            country_field_england,
        ]

        epc = session_data.get(epc_details_field)

        epc_band = epc.get("current-energy-rating")
        epc_date = epc.get("lodgement-date")

        try:
            working_epc_date = datetime.strptime(epc_date, "%Y-%m-%d")
            month_name = month_names[working_epc_date.month - 1]
            gds_epc_date = f"{working_epc_date.strftime('%-d')} {month_name} {working_epc_date.strftime('%Y')}"
        except ValueError as e:
            logger.error(e)
            gds_epc_date = ""

        current_month, next_month = utils.get_current_and_next_month_names(month_names)
        current_quarter_month, next_quarter_month = utils.get_current_and_next_quarter_month_names(month_names)

        context = {
            "epc_rating": epc_band.upper() if epc_band else "",
            "gds_epc_date": gds_epc_date,
            "epc_date": epc_date,
            "current_month": current_month,
            "next_month": next_month,
            "current_quarter_month": current_quarter_month,
            "next_quarter_month": next_quarter_month,
            "epc_display_options": schemas.epc_display_options_map,
            "address": address,
            "show_monthly_epc_update_details": show_monthly_epc_update_details,
        }
        return context

    def save_post_data(self, data, session_id, page_name):
        accept_suggested_epc = data.get(epc_accept_suggested_epc_field)
        epc_rating = data.get(epc_rating_field).upper()
        data[epc_rating_is_eligible_field] = (
            field_no if (epc_rating in ("A", "B", "C")) and (accept_suggested_epc == field_yes) else field_yes
        )
        return data


@register_page(no_epc_page)
class NoEpcView(PageView):
    def build_extra_context(self, request, session_id, page_name, data, is_change_page):
        session_data = interface.api.session.get_session(session_id)

        country = session_data.get(country_field)

        current_month, next_month = utils.get_current_and_next_month_names(month_names)
        current_quarter_month, next_quarter_month = utils.get_current_and_next_quarter_month_names(month_names)

        show_month_wording = country in [country_field_england, country_field_wales]

        return {
            "current_month": current_month,
            "next_month": next_month,
            "current_quarter_month": current_quarter_month,
            "next_quarter_month": next_quarter_month,
            "show_month_wording": show_month_wording,
        }

    def save_post_data(self, data, session_id, page_name):
        data[no_epc_field] = field_yes
        return data


@register_page(benefits_page)
class BenefitsView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        context = interface.api.session.get_session(session_id)
        return {"benefits_options": schemas.yes_no_options_map, "context": context}


@register_page(household_income_page)
class HouseholdIncomeView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"household_income_options": schemas.household_income_options_map}


@register_page(property_type_page)
class PropertyTypeView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"property_type_options": schemas.property_type_options_map}


@register_page(property_subtype_page)
class PropertySubtypeView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, property_type_page)
        property_type = data[property_type_field]
        return {
            "property_type": schemas.property_subtype_titles_options_map[property_type],
            "property_subtype_options": schemas.property_subtype_options_map[property_type],
        }


@register_page(number_of_bedrooms_page)
class NumberOfBedroomsView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"number_of_bedrooms_options": schemas.number_of_bedrooms_options_map}


@register_page(wall_type_page)
class WallTypeView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"wall_type_options": schemas.wall_type_options_map}


@register_page(wall_insulation_page)
class WallInsulationView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"wall_insulation_options": schemas.wall_insulation_options_map}


@register_page(loft_page)
class LoftView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"loft_options": schemas.loft_options_map}


@register_page(loft_access_page)
class LoftAccessView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"loft_access_options": schemas.loft_access_options_map}


@register_page(loft_insulation_page)
class LoftInsulationView(PageView):
    def build_extra_context(self, *args, **kwargs):
        return {"loft_insulation_options": schemas.loft_insulation_options_map}


@register_page(summary_page)
class SummaryView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        summary_lines = tuple(
            {
                "question": schemas.summary_map[question],
                "answer": self.get_answer(session_data, question),
                "change_url": self.get_change_url(session_id, page_name),
            }
            for page_name, question in self.get_summary_questions(session_data)
        )
        return {"summary_lines": summary_lines}

    def get_summary_questions(self, session_data):
        for page_name in calculate_journey(session_data, to_page=summary_page):
            if page_name in schemas.page_display_questions.keys():
                for question in schemas.page_display_questions[page_name]:
                    if self.show_question(session_data, question):
                        yield page_name, question

    def show_question(self, session_data, question):
        return question in schemas.summary_map

    def get_answer(self, session_data, question):
        answer = session_data.get(question)
        answers_map = schemas.check_your_answers_options_map.get(question)
        return answers_map[answer] if answers_map else answer

    def get_change_url(self, session_id, page_name):
        return reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=page_name))

    def handle_saved_answers(self, request, session_id, page_name, answers, is_change_page):
        supplier_redirect = unavailable_supplier_redirect(session_id)
        if supplier_redirect is not None:
            return supplier_redirect
        return super().handle_saved_answers(request, session_id, page_name, answers, is_change_page)


@register_page(schemes_page)
class SchemesView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        eligible_schemes = eligibility.calculate_eligibility(session_data)
        save_answer(session_id, schemes_page, {schemes_field: eligible_schemes})
        eligible_schemes = tuple(schemas.schemes_map[scheme] for scheme in eligible_schemes if not scheme == "ECO4")
        supplier_name = SupplierConverter(session_id).get_supplier_on_general_pages()

        is_in_park_home = session_data.get(park_home_field, field_no) == field_yes
        is_social_housing = session_data.get(own_property_field) == own_property_field_social_housing

        is_solid_walls = session_data.get(wall_type_field) in [
            wall_type_field_solid,
            wall_type_field_mix,
            wall_type_field_dont_know,
        ]
        is_cavity_walls = session_data.get(wall_type_field) in [
            wall_type_field_cavity,
            wall_type_field_mix,
            wall_type_field_dont_know,
        ]
        is_wall_insulation_present = not session_data.get(wall_insulation_field) in [
            wall_insulation_field_some,
            wall_insulation_field_no,
            wall_insulation_field_dont_know,
        ]
        is_not_on_benefits = session_data.get(benefits_field, field_no) == field_no
        is_income_above_threshold = (
            session_data.get(household_income_field, household_income_field_more_than_threshold)
            == household_income_field_more_than_threshold
        )
        is_loft_present = session_data.get(loft_field) == loft_field_yes
        is_there_access_to_loft = session_data.get(loft_access_field) == loft_access_field_yes
        is_loft_insulation_over_threshold = session_data.get(loft_insulation_field) in [
            loft_insulation_field_more_than_threshold,
            loft_insulation_field_dont_know,
        ]
        is_loft_insulation_under_threshold = session_data.get(loft_insulation_field) in [
            loft_insulation_field_less_than_threshold,
            loft_insulation_field_dont_know,
        ]
        show_park_home_text = is_in_park_home and not is_social_housing
        show_loft_insulation_text = (not show_park_home_text) and is_loft_present and is_there_access_to_loft

        text_flags = {
            "show_park_home_text": show_park_home_text,
            "show_cavity_wall_text": (not show_park_home_text) and is_cavity_walls and not is_wall_insulation_present,
            "show_solid_wall_text": (not show_park_home_text) and is_solid_walls and not is_wall_insulation_present,
            "show_room_in_roof_text": (not show_park_home_text) and not is_loft_present,
            "show_loft_insulation_text": show_loft_insulation_text,
            "show_contribution_text": show_park_home_text
            or ((not is_social_housing) and is_not_on_benefits and is_income_above_threshold),
            "show_loft_insulation_low_contribution_text": show_loft_insulation_text
            and is_loft_insulation_under_threshold,
            "show_loft_insulation_medium_contribution_text": show_loft_insulation_text
            and is_loft_insulation_over_threshold,
        }

        return {"eligible_schemes": eligible_schemes, "supplier_name": supplier_name, "text_flags": text_flags}

    def validate(self, request, session_id, page_name, data, is_change_page):
        session_data = interface.api.session.get_session(session_id)
        fields = page_compulsory_field_map.get(page_name, ())
        missing_fields = tuple(field for field in fields if not data.get(field))
        errors = {field: missing_item_errors[field] for field in missing_fields}
        is_park_home = session_data.get(park_home_field, field_no) == field_yes
        is_not_on_benefits = session_data.get(benefits_field, field_no) == field_no
        is_income_above_threshold = (
            session_data.get(household_income_field, household_income_field_more_than_threshold)
            == household_income_field_more_than_threshold
        )
        is_social_housing = session_data.get(own_property_field) == own_property_field_social_housing
        should_verify_contribution_checkbox = (is_park_home and not is_social_housing) or (
            (not is_social_housing) and is_not_on_benefits and is_income_above_threshold
        )
        if should_verify_contribution_checkbox:
            if not data.get("contribution_acknowledgement"):
                errors = {
                    **errors,
                    "contribution_acknowledgement": missing_item_errors["contribution_acknowledgement"],
                }
        if not data.get("ventilation_acknowledgement"):
            errors = {
                **errors,
                "ventilation_acknowledgement": missing_item_errors["ventilation_acknowledgement"],
            }
        return errors


@register_page(bulb_warning_page)
class BulbWarningPageView(PageView):
    def save_post_data(self, data, session_id, page_name):
        data[bulb_warning_page_field] = field_yes
        return data


@register_page(utility_warehouse_warning_page)
class UtilityWarehousePageView(PageView):
    def save_post_data(self, data, session_id, page_name):
        data[utility_warehouse_warning_page_field] = field_yes
        return data


@register_page(shell_warning_page)
class ShellWarningPageView(PageView):
    def save_post_data(self, data, session_id, page_name):
        data[shell_warning_page_field] = field_yes
        return data


@register_page("applications-closed")
class ApplicationsClosedView(PageView):
    def build_extra_context(self, session_id, *args, **kwargs):
        supplier = SupplierConverter(session_id).get_supplier_on_general_pages()
        return {"supplier": supplier}


@register_page(contact_details_page)
class ContactDetailsView(PageView):
    def build_extra_context(self, session_id, *args, **kwargs):
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


@register_page(confirm_and_submit_page)
class ConfirmSubmitView(PageView):
    def build_extra_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        summary_lines = tuple(
            {
                "question": schemas.confirm_sumbit_map[question],
                "answer": session_data.get(question),
                "change_url": self.get_change_url(session_id, page_name),
            }
            for page_name, question in self.get_confirm_submit_questions(session_data)
        )
        supplier = SupplierConverter(session_id).get_supplier_on_general_pages()
        return {"summary_lines": summary_lines, "supplier": supplier}

    def get_confirm_submit_questions(self, session_data):
        for page_name in calculate_journey(session_data, from_page=schemes_page, to_page=confirm_and_submit_page):
            if page_name in schemas.page_display_questions:
                for question in schemas.page_display_questions[page_name]:
                    yield page_name, question

    def get_change_url(self, session_id, page_name):
        return reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=page_name))

    def handle_saved_answers(self, request, session_id, page_name, answers, is_change_page):
        supplier_redirect = unavailable_supplier_redirect(session_id)
        if supplier_redirect is not None:
            return supplier_redirect
        interface.api.session.create_referral(session_id)
        save_answer(session_id, page_name, {"referral_created_at": str(timezone.now())})
        session_data = interface.api.session.get_session(session_id)
        session_data = SupplierConverter(session_id).replace_in_session_data(session_data)
        if session_data.get("email"):
            referral = portal.models.Referral.objects.get(session_id=session_id)
            session_data["referral_id"] = referral.formatted_referral_id
            email_handler.send_referral_confirmation_email(session_data, request.LANGUAGE_CODE)


@register_page(success_page)
class SuccessView(PageView):
    def build_extra_context(self, session_id, *args, **kwargs):
        supplier = SupplierConverter(session_id).get_supplier_on_success_page()
        session_data = interface.api.session.get_session(session_id)
        is_eco4_eligible = eco4 in calculate_eligibility(session_data)
        referral = portal.models.Referral.objects.get(session_id=session_id)
        return {
            "supplier": supplier,
            "referral_id": referral.formatted_referral_id,
            "is_eco4_eligible": is_eco4_eligible,
        }


@register_page(northern_ireland_ineligible_page)
class NorthernIrelandView(PageView):
    def save_get_data(self, data, session_id, page_name):
        # this is saved for analytics purposes
        # see https://github.com/UKGovernmentBEIS/help-to-heat-GBIS/commit/973f9a520c68d3b4b08ebab302614f1d030cec3e
        data[page_name_field] = page_name
        return data


@register_page(park_home_ineligible_page)
class ParkHomeIneligiblePage(PageView):
    def save_get_data(self, data, session_id, page_name):
        data[page_name_field] = page_name
        return data


@register_page(epc_ineligible_page)
class EpcIneligiblePage(PageView):
    def save_get_data(self, data, session_id, page_name):
        data[page_name_field] = page_name
        return data


@register_page(property_ineligible_page)
class IneligiblePage(PageView):
    def save_get_data(self, data, session_id, page_name):
        data[page_name_field] = page_name
        return data


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
        "govuk_url": govuk_start_page_url,
    }
    return render(request, template_name="frontdoor/privacy-policy.html", context=context)


def accessibility_statement_view(request, session_id=None, page_name=None):
    prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
    context = {
        "session_id": session_id,
        "page_name": page_name,
        "prev_url": prev_page_url,
        "govuk_url": govuk_start_page_url,
    }
    return render(request, template_name="frontdoor/accessibility-statement.html", context=context)
