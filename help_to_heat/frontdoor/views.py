import uuid

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from marshmallow import ValidationError

from help_to_heat import utils

from ..portal import email_handler
from . import eligibility, interface, schemas

page_map = {}


page_compulsory_field_map = {
    "country": ("country",),
    "own-property": ("own_property",),
    "address": ("address_line_1", "postcode"),
    "address-select": ("uprn",),
    "address-manual": ("address_line_1", "town_or_city", "postcode"),
    "council-tax-band": ("council_tax_band",),
    "epc": ("accept_suggested_epc",),
    "benefits": ("benefits",),
    "household-income": ("household_income",),
    "property-type": ("property_type",),
    "number-of-bedrooms": ("number_of_bedrooms",),
    "wall-type": ("wall_type",),
    "wall-insulation": ("wall_insulation",),
    "loft": ("loft",),
    "loft-access": ("loft_access",),
    "loft-insulation": ("loft_insulation",),
    "supplier": ("supplier",),
    "contact-details": ("first_name", "last_name"),
    "confirm-and-submit": ("permission",),
}

missing_item_errors = {
    "country": "Select where the property is located",
    "own_property": "Select if you own the property",
    "address_line_1": "Enter Address line 1",
    "postcode": "Enter a postcode",
    "uprn": "Select your address",
    "town_or_city": "Enter your Town or city",
    "council_tax_band": "Enter the Council Tax Band of the property",
    "accept_suggested_epc": "Select if your EPC rating is correct or not, or that you don’t know",
    "benefits": "Select if anyone in your household is receiving any benefits listed below",
    "household_income": "Select your household income",
    "property_type": "Select your property type",
    "number_of_bedrooms": "Select the number of bedrooms the property has",
    "wall_type": "Select the type of walls the property has",
    "wall_insulation": "Select if the walls of the property are insulated or not, or if you don’t know",
    "loft": "Select if you have a loft that has been converted into a room or not",
    "loft_access": "Select whether or not you have access to the loft",
    "loft_insulation": "Select whether or not your loft is fully insulated",
    "supplier": "Select your home energy supplier from the list below",
    "first_name": "Enter your first name",
    "last_name": "Enter your last name",
    "email": "Enter your address",
    "contact_number": "Enter your contact number",
    "permission": "Please confirm that you agree to the use of your information by checking this box",
}


def register_page(name):
    def _inner(func):
        page_map[name] = func
        return func

    return _inner


def homepage_view(request):
    session_id = uuid.uuid4()
    next_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="country"))
    context = {
        "next_url": next_url,
    }
    return render(request, template_name="frontdoor/homepage.html", context=context)


def get_prev_next_page_name(page_name):
    if page_name in schemas.page_prev_next_map:
        prev_page_name = schemas.page_prev_next_map[page_name]["prev"]
        next_page_name = schemas.page_prev_next_map[page_name]["next"]
    else:
        assert page_name in schemas.page_order, page_name
        page_index = schemas.page_order.index(page_name)
        if page_index == 0:
            prev_page_name = "homepage"
        else:
            prev_page_name = schemas.pages[page_index - 1]
        if page_index + 1 == len(schemas.pages):
            next_page_name = None
        else:
            next_page_name = schemas.pages[page_index + 1]
    return prev_page_name, next_page_name


def get_prev_next_urls(session_id, page_name):
    prev_page_name, next_page_name = get_prev_next_page_name(page_name)
    if prev_page_name == "homepage":
        prev_page_url = reverse("frontdoor:homepage")
    else:
        prev_page_url = prev_page_name and reverse(
            "frontdoor:page", kwargs=dict(session_id=session_id, page_name=prev_page_name)
        )
    next_page_url = next_page_name and reverse(
        "frontdoor:page", kwargs=dict(session_id=session_id, page_name=next_page_name)
    )
    return prev_page_url, next_page_url


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
        extra_context = self.get_context(request=request, session_id=session_id, page_name=page_name, data=data)
        context = {
            "data": data,
            "session_id": session_id,
            "page_name": page_name,
            "errors": errors,
            "prev_url": prev_page_url,
            "next_url": next_page_url,
            **extra_context,
        }
        return render(request, template_name=f"frontdoor/{page_name}.html", context=context)

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
            _, next_page_name = get_prev_next_page_name(page_name)
        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

    def validate(self, request, session_id, page_name, data, is_change_page):
        fields = page_compulsory_field_map.get(page_name, ())
        missing_fields = tuple(field for field in fields if not data.get(field))
        errors = {field: missing_item_errors[field] for field in missing_fields}
        return errors


@register_page("country")
class CountryView(PageView):
    def get_context(self, *args, **kwargs):
        return {"country_options": schemas.country_options}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        if data["country"] == "Northern Ireland":
            return redirect("frontdoor:page", session_id=session_id, page_name="northern-ireland")
        else:
            return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("own-property")
class OwnPropertyView(PageView):
    def get_context(self, *args, **kwargs):
        return {"own_property_options_map": schemas.own_property_options_map}


@register_page("address")
class AddressView(PageView):
    def handle_post(self, request, session_id, page_name, data, is_change_page):
        return redirect("frontdoor:page", session_id=session_id, page_name="address-select")


@register_page("address-select")
class AddressSelectView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "address")
        text = f"{data['address_line_1'], data['postcode']}"
        addresses = interface.api.address.find_addresses(text)
        uprn_options = tuple({"value": a["uprn"], "label": a["address"]} for a in addresses)
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


@register_page("council-tax-band")
class CouncilTaxBandView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "country")
        selected_country = data.get("country")
        council_tax_bands = schemas.council_tax_band_options
        if selected_country == "Wales":
            council_tax_bands = schemas.welsh_council_tax_band_options
        return {"council_tax_band_options": council_tax_bands}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        session_data = interface.api.session.get_session(session_id)
        if session_data.get("country") == "Scotland":
            return redirect("frontdoor:page", session_id=session_id, page_name="benefits")
        else:
            return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("epc")
class EpcView(PageView):
    def get_context(self, request, session_id, page_name, data):
        session_data = interface.api.session.get_session(session_id)
        uprn = session_data.get("uprn")
        address = session_data.get("address")
        if uprn:
            epc = interface.api.epc.get_epc(uprn)
        else:
            epc = {}
        context = {
            "epc_rating": epc.get("rating"),
            "epc_date": epc.get("date"),
            "epc_display_options": schemas.epc_display_options,
            "address": address,
        }
        return context

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name)
        epc_rating = data.get("epc_rating")
        accept_suggested_epc = data.get("accept_suggested_epc")
        if not epc_rating:
            return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)

        if (epc_rating in ("A", "B", "C")) and (accept_suggested_epc == "Yes"):
            return redirect("frontdoor:page", session_id=session_id, page_name="epc-ineligible")

        choice = data["accept_suggested_epc"]
        if choice in ("Yes", "Not found"):
            prev_page_name, next_page_name = get_prev_next_page_name(page_name)
            return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)
        else:
            return redirect("frontdoor:page", session_id=session_id, page_name="epc-disagree")


@register_page("epc-disagree")
class EpcDisagreeView(PageView):
    def get(self, request, session_id, page_name, errors=None, is_change_page=False):
        if not errors:
            errors = {}
        data = {}
        prev_page_url, next_page_url = get_prev_next_urls(session_id, page_name)
        extra_context = self.get_context(request=request, session_id=session_id, page_name=page_name, data=data)
        context = {
            "data": data,
            "session_id": session_id,
            "errors": errors,
            "prev_url": prev_page_url,
            "next_url": next_page_url,
            **extra_context,
        }
        return render(request, template_name=f"frontdoor/{page_name}.html", context=context)

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = interface.api.session.save_answer(session_id, "epc", request.POST.dict())
        return data


@register_page("benefits")
class BenefitsView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        context = interface.api.session.get_session(session_id)
        return {"benefits_options": schemas.yes_no_options, "context": context}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        session_data = interface.api.session.get_session(session_id)
        eligible_schemes = eligibility.calculate_eligibility(session_data)
        if not eligible_schemes:
            return redirect("frontdoor:page", session_id=session_id, page_name="ineligible")
        else:
            return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("household-income")
class HouseholdIncomeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"household_income_options": schemas.household_income_options}


@register_page("property-type")
class PropertyTypeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"property_type_options": schemas.property_type_options}


@register_page("property-subtype")
class PropertySubtypeView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        data = interface.api.session.get_answer(session_id, "property-type")
        property_type = data["property_type"]
        return {
            "property_type": property_type,
            "property_subtype_options": schemas.property_subtype_options_map[property_type],
        }


@register_page("number-of-bedrooms")
class NumberOfBedroomsView(PageView):
    def get_context(self, *args, **kwargs):
        return {"number_of_bedrooms_options": schemas.number_of_bedrooms_options}


@register_page("wall-type")
class WallTypeView(PageView):
    def get_context(self, *args, **kwargs):
        return {"wall_type_options": schemas.wall_type_options}


@register_page("wall-insulation")
class WallInsulationView(PageView):
    def get_context(self, *args, **kwargs):
        return {"wall_insulation_options": schemas.wall_insulation_options}


@register_page("loft")
class LoftView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_options": schemas.loft_options}

    def save_data(self, request, session_id, page_name, *args, **kwargs):
        data = request.POST.dict()
        loft = data.get("loft")
        if loft == "No, I don't have a loft or my loft has been converted into a room":
            data["loft_access"] = "No loft"
            data["loft_insulation"] = "No loft"
        data = interface.api.session.save_answer(session_id, page_name, data)
        return data

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        prev_page_name, next_page_name = get_prev_next_page_name(page_name)
        loft = data.get("loft")
        if loft == "No, I don't have a loft or my loft has been converted into a room":
            next_page_name = "summary"
        return redirect("frontdoor:page", session_id=session_id, page_name=next_page_name)


@register_page("loft-access")
class LoftAccessView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_access_options": schemas.loft_access_options}


@register_page("loft-insulation")
class LoftInsulationView(PageView):
    def get_context(self, *args, **kwargs):
        return {"loft_insulation_options": schemas.loft_insulation_options}

    def get_prev_next_urls(self, session_id, page_name):
        loft_data = interface.api.session.get_answer(session_id, "loft")

        if loft_data.get("loft", None) == "Yes, I have a loft that hasn't been converted into a room":
            _, next_page_url = get_prev_next_urls(session_id, page_name)
            prev_page_url = reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name="loft-insulation"))
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
                "answer": session_data.get(question),
                "change_url": reverse("frontdoor:change-page", kwargs=dict(session_id=session_id, page_name=page_name)),
            }
            for page_name, questions in schemas.household_pages.items()
            for question in questions
            if question in session_data
        )
        return {"summary_lines": summary_lines}


@register_page("schemes")
class SchemesView(PageView):
    def get_context(self, request, session_id, *args, **kwargs):
        session_data = interface.api.session.get_session(session_id)
        eligible_schemes = eligibility.calculate_eligibility(session_data)
        _ = interface.api.session.save_answer(session_id, "schemes", {"schemes": eligible_schemes})
        eligible_schemes = tuple(scheme for scheme in eligible_schemes if not scheme == "Energy Company Obligation 4")
        return {"eligible_schemes": eligible_schemes}


@register_page("supplier")
class SupplierView(PageView):
    def get_context(self, *args, **kwargs):
        return {"supplier_options": schemas.supplier_options}


@register_page("contact-details")
class ContactDetailsView(PageView):
    def get_context(self, session_id, *args, **kwargs):
        supplier_data = interface.api.session.get_answer(session_id, "supplier")
        return {"supplier": supplier_data["supplier"]}

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
        supplier_data = interface.api.session.get_answer(session_id, "supplier")
        supplier = supplier_data["supplier"]
        return {"summary_lines": summary_lines, "supplier": supplier}

    def handle_post(self, request, session_id, page_name, data, is_change_page):
        interface.api.session.create_referral(session_id)
        session_data = interface.api.session.get_session(session_id)
        if session_data.get("email"):
            email_handler.send_referral_confirmation_email(session_data)
        return super().handle_post(request, session_id, page_name, data, is_change_page)


@register_page("success")
class SuccessView(PageView):
    def get_context(self, session_id, *args, **kwargs):
        supplier_data = interface.api.session.get_answer(session_id, "supplier")
        return {"supplier": supplier_data["supplier"]}


def page_view(request, session_id, page_name):
    if page_name in page_map:
        return page_map[page_name](request, session_id, page_name)

    prev_page_url, next_page_url = get_prev_next_urls(session_id, page_name)
    context = {"session_id": session_id, "page_name": page_name, "prev_url": prev_page_url}
    return render(request, template_name=f"frontdoor/{page_name}.html", context=context)


def change_page_view(request, session_id, page_name):
    assert page_name in page_map
    return page_map[page_name](request, session_id, page_name, is_change_page=True)


class FeedbackView(utils.MethodDispatcher):
    def get(self, request, session_id=None, page_name=None):
        template_name = "frontdoor/feedback.html"
        prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
        context = {
            "session_id": session_id,
            "page_name": page_name,
            "prev_url": prev_page_url,
            "multichoice_options": schemas.multichoice_options,
        }
        return render(request, template_name=template_name, context=context)

    def post(self, request, session_id=None, page_name=None):
        data = request.POST.dict()
        interface.api.feedback.save_feedback(session_id, page_name, data)
        if session_id and page_name:
            return redirect("frontdoor:feedback-thanks", session_id=session_id, page_name=page_name)
        else:
            return redirect("frontdoor:feedback-thanks")


def feedback_thanks_view(request, session_id=None, page_name=None):
    template_name = "frontdoor/feedback-thanks.html"
    prev_page_url = page_name and reverse("frontdoor:page", kwargs=dict(session_id=session_id, page_name=page_name))
    context = {"session_id": session_id, "page_name": page_name, "prev_url": prev_page_url}
    return render(request, template_name=template_name, context=context)


def cookies_view(request):
    return render(request, template_name="frontdoor/cookies.html")


def data_layer_js_view(request):
    return render(request, "dataLayer.js", {"gtag_id": settings.GTAG_ID}, content_type="application/x-javascript")


def privacy_policy_view(request):
    return render(request, template_name="frontdoor/privacy-policy.html")


def accessibility_statement_view(request):
    return render(request, template_name="frontdoor/accessibility-statement.html")
