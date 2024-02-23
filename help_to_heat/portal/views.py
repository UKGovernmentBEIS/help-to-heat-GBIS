import datetime
import logging
import subprocess
import urllib.parse

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


class ParseDateError:
    def __init__(self, message, error_parts=("day", "month", "year")):
        self.message = message
        self.error_parts = error_parts


def parse_date(request, date_name):
    day_input = request.POST.get(date_name + "-day", "")
    month_input = request.POST.get(date_name + "-month", "")
    year_input = request.POST.get(date_name + "-year", "")
    date_parts = [("day", day_input), ("month", month_input), ("year", year_input)]

    empty_parts = []
    for name, value in date_parts:
        if value.strip() == "":
            empty_parts.append(name)

    if len(empty_parts) == 3:
        return ParseDateError(f"Enter the {date_name} date", empty_parts), None

    if len(empty_parts) > 0:
        list_of_parts = " and ".join(empty_parts)
        return ParseDateError(f"The {date_name} date must include a {list_of_parts}", empty_parts), None

    non_numeric_parts = []
    for name, value in date_parts:
        if not value.isdigit():
            non_numeric_parts.append(name)

    if len(non_numeric_parts) > 0:
        last_part = non_numeric_parts[-1]
        other_parts = non_numeric_parts[:-1]
        list_of_parts = last_part if not other_parts else f"{', '.join(other_parts)} and {last_part}"
        number_or_numbers = "numbers" if other_parts else "a number"
        return (
            ParseDateError(f"The {date_name} date’s {list_of_parts} must be {number_or_numbers}", non_numeric_parts),
            None,
        )

    if len(year_input) != 4:
        return ParseDateError(f"The {date_name} date’s year must include 4 numbers", ["year"]), None

    day = int(day_input)
    month = int(month_input)
    year = int(year_input)

    impossible_parts = []
    if day < 1 or day > 31:
        impossible_parts.append("day")
    if month < 1 or month > 12:
        impossible_parts.append("month")

    if len(impossible_parts) > 0:
        return ParseDateError(f"The {date_name} date must be a real date", impossible_parts), None

    try:
        date = datetime.date(year, month, day)
    except ValueError:
        return ParseDateError(f"The {date_name} date must be a real date"), None

    if date > datetime.date.today():
        return ParseDateError(f"The {date_name} date must be today or in the past"), None

    return None, date


def parse_date_range(request):
    start_date_error, start_date = parse_date(request, "start")
    end_date_error, end_date = parse_date(request, "end")

    if start_date_error is not None or end_date_error is not None:
        errors = {"start": start_date_error, "end": end_date_error}
        return errors, None, None

    if start_date > end_date:
        end_date_error = ParseDateError("The end date must be the same as or after the start date")
        errors = {"end": end_date_error}
        return errors, None, None

    return None, start_date, end_date


@require_http_methods(["GET", "POST"])
@decorators.requires_service_manager
def service_manager_homepage_view(request):
    data = {}
    errors = {}

    if request.method == "POST":
        date_errors, start_date, end_date = parse_date_range(request)

        if date_errors is None:
            params = {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")}
            query = urllib.parse.urlencode(params)
            return redirect(f"{reverse('portal:referrals-range-download')}?{query}")

        data_keys = ["start-day", "start-month", "start-year", "end-day", "end-month", "end-year"]
        for data_key in data_keys:
            data[data_key] = request.POST.get(data_key, None)

        for name, error in date_errors.items():
            if error is None:
                continue
            first_error_part = error.error_parts[0]
            error_key = f"{name}-{first_error_part}"
            errors[error_key] = error.message
    else:
        date_errors = {}

    template = "portal/service-manager/homepage.html"

    suppliers_to_hide = ["Bulb, now part of Octopus Energy", "ESB"]
    suppliers = [supplier for supplier in models.Supplier.objects.all() if supplier.name not in suppliers_to_hide]
    suppliers.sort(key=lambda supplier: supplier.name)
    data["suppliers"] = suppliers

    return render(
        request,
        template_name=template,
        context={"request": request, "data": data, "errors": errors, "date_errors": date_errors},
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
