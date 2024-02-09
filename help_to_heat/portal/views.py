import logging
import subprocess
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
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


def parse_date(year: str, month: str, day: str):
    if year == "":
        return "year-required", "year", None
    if month == "":
        return "month-required", "month", None
    if day == "":
        return "day-required", "day", None

    if not year.isdecimal():
        return "year-integer", "year", None
    if not month.isdecimal():
        return "month-integer", "month", None
    if not day.isdecimal():
        return "day-integer", "day", None

    year = int(year)
    month = int(month)
    day = int(day)

    def try_parse_date(year, month, day):
        try:
            return date(year, month, day)
        except ValueError:
            return None

    check_date = try_parse_date(year, month, day)

    if check_date is None:
        return "invalid", "all", None

    today = date.today()

    if check_date > today:
        return "future", "all", None

    return None, check_date


@require_http_methods(["GET", "POST"])
@decorators.requires_service_manager
def service_manager_homepage_view(request):
    errors = {}
    if request.method == "POST":
        date_from_error, date_from_error_location, date_from = parse_date(
            request.POST.get("from-year", None),
            request.POST.get("from-month", None),
            request.POST.get("from-day", None)
        )
        date_to_error, date_to_error_location, date_to = parse_date(
            request.POST.get("to-year", None),
            request.POST.get("to-month", None),
            request.POST.get("to-day", None)
        )

        if date_from_error:
            errors["from"] = date_from_error
            if date_from_error_location in ["all", "year"]:
                errors["from-year"] = True
            if date_from_error_location in ["all", "month"]:
                errors["from-month"] = True
            if date_from_error_location in ["all", "day"]:
                errors["from-day"] = True
        if date_to_error:
            errors["to"] = date_to_error
            if date_to_error_location in ["all", "year"]:
                errors["to-year"] = True
            if date_to_error_location in ["all", "month"]:
                errors["to-month"] = True
            if date_to_error_location in ["all", "day"]:
                errors["to-day"] = True

    template = "portal/service-manager/homepage.html"
    suppliers_to_hide = ["Bulb, now part of Octopus Energy", "ESB"]
    suppliers = [supplier for supplier in models.Supplier.objects.all() if supplier.name not in suppliers_to_hide]
    suppliers.sort(key=lambda supplier: supplier.name)
    data = {
        "suppliers": suppliers
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
