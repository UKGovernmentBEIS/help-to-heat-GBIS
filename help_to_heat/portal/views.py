import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

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


@require_http_methods(["GET"])
@login_required(login_url="portal:unauthorised")
def homepage_view(request):
    user = request.user
    if user.is_service_manager:
        return service_manager_homepage_view(request)
    elif user.is_team_leader:
        return team_leader_homepage_view(request)
    elif user.is_team_member:
        return team_member_homepage_view(request)
    else:
        return redirect("portal:unauthorised")


@require_http_methods(["GET"])
@decorators.requires_service_manager
def service_manager_homepage_view(request):
    template = "portal/service-manager/homepage.html"
    suppliers = models.Supplier.objects.all()
    data = {
        "suppliers": suppliers,
    }
    return render(
        request,
        template_name=template,
        context={"request": request, "data": data},
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
    archives = models.ReferralDownload.objects.filter(referral_download__supplier=supplier).order_by("-created_at")
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


@require_http_methods(["GET"])
def epc_page(request):
    epc_count = models.EpcRating.objects.count()
    template = "portal/epc-page.html"
    return render(
        request,
        template_name=template,
        context={"epc_count": epc_count},
    )
