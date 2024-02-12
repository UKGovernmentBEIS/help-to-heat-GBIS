import datetime
import logging
import subprocess

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from help_to_heat import utils

from . import decorators, models

logger = logging.getLogger("django.request")
logger.setLevel(logging.ERROR)


@require_http_methods(["GET"])
@login_required(login_url="portal:unauthorised")
def index_view(request):
    return render(
        request,
        template_name="index.html",
        context={"request": request},
    )


@require_http_methods(["GET"])
def unauthorised_view(request):
    return render(request, "portal/unauthorised.html", {}, status=403)


@require_http_methods(["GET", "POST"])
@login_required(login_url="portal:unauthorised")
def homepage_view(request):
    user = request.user
    if request.method == "GET":
        if user.is_service_manager:
            return service_manager_homepage_view(request)
        elif user.is_team_leader:
            return team_leader_homepage_view(request)
        elif user.is_team_member:
            return team_member_homepage_view(request)
    elif request.method == "POST":
        if user.is_service_manager:
            return service_manager_homepage_view(request)

    return redirect("portal:unauthorised")


def parse_date_input(date_input: str, min, max):
    if date_input == "":
        return True, None
    if not date_input.isdecimal():
        return True, None
    date_input = int(date_input)
    if date_input < min or date_input > max:
        return True, None
    return False, date_input


def generate_error(error):
    return {
        "error_messages": [error],
        "year": True,
        "month": True,
        "day": True
    }


def parse_date(year: str, month: str, day: str):
    error_messages = []

    year_error, year = parse_date_input(year, datetime.MINYEAR, datetime.MAXYEAR)
    if year_error:
        error_messages.append("%s must include a valid year")
        year_error = True

    month_error, month = parse_date_input(month, 1, 12)
    if month_error:
        error_messages.append("%s must include a valid month")
        month_error = True

    day_error, day = parse_date_input(day, 1, 31)
    if day_error:
        error_messages.append("%s must include a valid day")
        day_error = True

    if error_messages:
        return {
            "error_messages": error_messages, "year": year_error, "month": month_error, "day": day_error
        }, None

    def try_parse_date(year, month, day):
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None

    check_date = try_parse_date(year, month, day)

    if check_date is None:
        return generate_error("%s must be a real date"), None

    today = datetime.date.today()

    if check_date > today:
        return generate_error("%s must be today or in the past"), None

    return None, check_date


def parse_date_range(from_year, from_month, from_day, to_year, to_month, to_day):
    errors = {}
    date_from_error, date_from = parse_date(
        from_year,
        from_month,
        from_day,
    )
    date_to_error, date_to = parse_date(
        to_year,
        to_month,
        to_day
    )
    errors["from"] = date_from_error
    errors["to"] = date_to_error
    if date_from_error is not None or date_to_error is not None:
        return errors, None, None

    if date_from > date_to:
        errors["to"] = generate_error("%s must be the same as or after From")
        return errors, None, None

    return None, date_from, date_to


@require_http_methods(["GET", "POST"])
@decorators.requires_service_manager
def service_manager_homepage_view(request):
    errors = {}
    if request.method == "POST":
        date_range_error, date_from, date_to = parse_date_range(
            request.POST.get("from-year", None),
            request.POST.get("from-month", None),
            request.POST.get("from-day", None),
            request.POST.get("to-year", None),
            request.POST.get("to-month", None),
            request.POST.get("to-day", None)
        )

        if date_range_error is None:
            # ensure no extra data is sent as query params
            expected_keys = ["from-year", "from-month", "from-day", "to-year", "to-month", "to-day"]

            query_params = "&".join(
                [f"{key}={value}" for (key, value) in request.POST.items() if key in expected_keys]
            )

            return redirect(f"{reverse('portal:referrals-range-download')}?{query_params}")

        errors = {**date_range_error}


    template = "portal/service-manager/homepage.html"
    suppliers_to_hide = ["Bulb, now part of Octopus Energy", "ESB"]
    suppliers = [supplier for supplier in models.Supplier.objects.all() if supplier.name not in suppliers_to_hide]
    suppliers.sort(key=lambda supplier: supplier.name)
    data = {
        "suppliers": suppliers,
    }
    return render(
        request,
        template_name=template,
        context={"request": request, "data": data, "errors": errors, "previous": request.POST},
    )


@require_http_methods(["GET"])
@decorators.requires_team_leader
def team_leader_homepage_view(request):
    template = "portal/team-leader/homepage.html"
    user = request.user
    supplier = user.supplier
    team_members = models.User.objects.filter(supplier=supplier).filter(role__in=("TEAM_LEADER", "TEAM_MEMBER")).all()
    data = {
        "team_members": team_members,
    }
    referrals = models.Referral.objects.filter(referral_download=None, supplier=supplier)
    unread_leads = referrals.count()
    archives = (
        models.ReferralDownload.objects.filter(referral_download__supplier=supplier).order_by("-created_at").distinct()
    )
    data = {"supplier": supplier, "unread_leads": unread_leads, "archives": archives, **data}
    return render(
        request,
        template_name=template,
        context={"request": request, "data": data},
    )


@require_http_methods(["GET"])
@decorators.requires_team_member
def team_member_homepage_view(request):
    template = "portal/team-member/homepage.html"
    user = request.user
    supplier = user.supplier
    referrals = models.Referral.objects.filter(referral_download=None, supplier=supplier)
    unread_leads = referrals.count()
    archives = models.ReferralDownload.objects.filter(referral_download__supplier=supplier).order_by("-created_at")
    data = {"supplier": supplier, "unread_leads": unread_leads, "archives": archives}
    return render(
        request,
        template_name=template,
        context={"request": request, "data": data},
    )


@require_http_methods(["GET"])
def healthcheck_view(request):
    _ = models.User.objects.exists()
    data = {"healthy": True, "datetime": timezone.now()}
    return JsonResponse(data, status=201)


@require_http_methods(["GET", "POST"])
class EPCUploadView(utils.MethodDispatcher):
    args = (
        "/usr/local/bin/python",
        "/app/manage.py",
        "load_epc_ratings",
        "--url",
    )

    def get(self, request):
        with connection.cursor() as cursor:
            query = "SELECT COUNT(*) FROM portal_epcrating"
            cursor.execute(query)
            epc_count = cursor.fetchone()
        template = "portal/epc-page.html"
        return render(
            request,
            template_name=template,
            context={"epc_count": epc_count},
        )

    def post(self, request):
        url = request.POST["url"]
        cmd_args = self.args + (url,)
        subprocess.Popen(cmd_args)
        return redirect("/portal/epc-uploads")
