from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from help_to_heat.portal import email_handler, models

from .decorators import requires_service_manager, requires_team_leader


@require_http_methods(["GET", "POST"])
@requires_service_manager
def add_supplier_view(request):
    if request.method == "GET":
        return render(request, "portal/service-manager/add-supplier.html", {})
    else:
        supplier_name = request.POST.get("supplier_name")
        new_supplier = models.Supplier(name=supplier_name, is_disabled=False)
        new_supplier.save()
        return redirect("portal:homepage")


@require_http_methods(["GET", "POST"])
@requires_service_manager
def edit_supplier_view(request, supplier_id):
    if request.method == "GET":
        supplier = models.Supplier.objects.get(pk=supplier_id)
        return render(request, "portal/service-manager/edit-supplier.html", {"supplier": supplier})
    else:
        supplier = models.Supplier.objects.get(pk=supplier_id)
        supplier.name = request.POST.get("supplier_name")
        supplier.save()
        return redirect("portal:homepage")


@require_http_methods(["GET", "POST"])
@requires_service_manager
def change_supplier_disabled_status_view(request, supplier_id):
    if request.method == "GET":
        supplier = models.Supplier.objects.get(pk=supplier_id)
        return render(request, "portal/service-manager/disable-supplier-confirmation.html", {"supplier": supplier})
    else:
        supplier = models.Supplier.objects.get(pk=supplier_id)
        supplier.is_disabled = not supplier.is_disabled
        supplier.save()
        return redirect("portal:homepage")


@require_http_methods(["GET"])
@requires_service_manager
def supplier_team_leads_view(request, supplier_id):
    if request.method == "GET":
        supplier = models.Supplier.objects.get(pk=supplier_id)
        users = supplier.user_set.filter(role="TEAM_LEADER").all()
        return render(
            request, "portal/service-manager/supplier-team-lead-list.html", {"users": users, "supplier": supplier}
        )


@require_http_methods(["GET", "POST"])
@requires_service_manager
def supplier_team_leads_add_view(request, supplier_id):
    if request.method == "GET":
        supplier = models.Supplier.objects.get(pk=supplier_id)
        return render(request, "portal/service-manager/add-supplier-team-lead.html", {"supplier": supplier})
    else:
        supplier = models.Supplier.objects.get(pk=supplier_id)
        leader_name = request.POST.get("team-leader-name")
        leader_email = request.POST.get("team-leader-email")

        user, _ = models.User.objects.get_or_create(email=leader_email)
        user.full_name = leader_name
        user.role = "TEAM_LEADER"
        user.supplier = supplier
        user.save()
        email_handler.send_invite_email(user)
        return redirect("portal:supplier-team-leads", supplier.id)


@require_http_methods(["GET", "POST"])
@requires_service_manager
def supplier_team_leads_edit_view(request, supplier_id, user_id):
    if request.method == "GET":
        user = models.User.objects.get(pk=user_id)
        supplier = models.Supplier.objects.get(pk=supplier_id)
        return render(
            request, "portal/service-manager/edit-supplier-team-lead.html", {"supplier": supplier, "user": user}
        )
    else:
        user = models.User.objects.get(pk=user_id)
        supplier = models.Supplier.objects.get(pk=supplier_id)
        leader_name = request.POST.get("team-leader-name")

        user.full_name = leader_name
        user.save()
        return redirect("portal:supplier-team-leads", supplier.id)


@require_http_methods(["GET", "POST"])
@requires_service_manager
def change_supplier_team_leads_disable_status_view(request, supplier_id, user_id):
    if request.method == "GET":
        supplier = models.Supplier.objects.get(pk=supplier_id)
        user = models.User.objects.get(pk=user_id)
        return render(
            request, "portal/service-manager/disable-team-lead-confirmation.html", {"supplier": supplier, "user": user}
        )
    else:
        user = models.User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        return redirect("portal:supplier-team-leads", supplier_id)


@require_http_methods(["GET", "POST"])
@requires_team_leader
def team_member_add_role_view(request, supplier_id):
    if request.method == "GET":
        return render(request, "portal/team-leader/add-user-role-select.html", {"supplier_id": supplier_id})
    else:
        user_role = request.POST.get("team-role")
        return redirect("portal:add-user-details-select", user_role=user_role, supplier_id=supplier_id)


@require_http_methods(["GET", "POST"])
@requires_team_leader
def team_member_add_details_view(request, supplier_id, user_role):
    if request.method == "GET":
        return render(
            request, "portal/team-leader/add-user-details.html", {"user_role": user_role, "supplier_id": supplier_id}
        )
    else:
        supplier = models.Supplier.objects.get(pk=supplier_id)
        user_name = request.POST.get("user-name")
        user_email = request.POST.get("user-email")

        user, _ = models.User.objects.get_or_create(email=user_email)
        user.full_name = user_name
        user.role = user_role
        user.supplier = supplier
        user.save()
        email_handler.send_invite_email(user)
        return redirect("portal:homepage")


@require_http_methods(["GET"])
@requires_team_leader
def team_member_details_view(request, supplier_id, user_id):
    user = models.User.objects.get(pk=user_id)
    return render(request, "portal/team-leader/view-user-details.html", {"supplier_id": supplier_id, "user": user})


@require_http_methods(["GET", "POST"])
@requires_team_leader
def team_member_change_status_view(request, supplier_id, user_id):
    if request.method == "GET":
        user = models.User.objects.get(pk=user_id)
        return render(
            request,
            "portal/team-leader/confirm-change-team-member-status.html",
            {"supplier_id": supplier_id, "user": user},
        )
    else:
        user = models.User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        return redirect("portal:user-details", supplier_id, user_id)


@require_http_methods(["GET", "POST"])
@requires_team_leader
def team_member_edit_view(request, supplier_id, user_id):
    if request.method == "GET":
        user = models.User.objects.get(pk=user_id)
        return render(request, "portal/team-leader/edit-user-details.html", {"supplier_id": supplier_id, "user": user})
    else:
        user_name = request.POST.get("user-name")
        team_role = request.POST.get("team-role")
        user, _ = models.User.objects.get_or_create(pk=user_id)
        user.full_name = user_name
        user.role = team_role
        user.save()
        return redirect("portal:user-details", supplier_id, user_id)
