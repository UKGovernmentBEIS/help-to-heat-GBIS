from django.urls import include, path

from . import (
    authentication_views,
    download_views,
    supplier_and_user_management_views,
    views,
)

portal_patterns = [
    path("", views.homepage_view, name="homepage"),
    path("unauthorised/", views.unauthorised_view, name="unauthorised"),
    path("add-supplier/", supplier_and_user_management_views.add_supplier_view, name="add-supplier"),
    path(
        "supplier/<uuid:supplier_id>/edit/",
        supplier_and_user_management_views.edit_supplier_view,
        name="edit-supplier",
    ),
    path(
        "supplier/<uuid:supplier_id>/change-status/",
        supplier_and_user_management_views.change_supplier_disabled_status_view,
        name="change-supplier-disabled-status",
    ),
    path(
        "supplier/<uuid:supplier_id>/team-leads/",
        supplier_and_user_management_views.supplier_team_leads_view,
        name="supplier-team-leads",
    ),
    path(
        "supplier/<uuid:supplier_id>/team-leads/add/",
        supplier_and_user_management_views.supplier_team_leads_add_view,
        name="supplier-team-leads-add",
    ),
    path(
        "supplier/<uuid:supplier_id>/team-leads/<uuid:user_id>/edit/",
        supplier_and_user_management_views.supplier_team_leads_edit_view,
        name="supplier-team-leads-edit",
    ),
    path(
        "supplier/<uuid:supplier_id>/team-leads/<uuid:user_id>/change-status/",
        supplier_and_user_management_views.change_supplier_team_leads_disable_status_view,
        name="change-supplier-team-lead-status",
    ),
    path(
        "supplier/<uuid:supplier_id>/user/add/",
        supplier_and_user_management_views.team_member_add_role_view,
        name="add-user-role-select",
    ),
    path(
        "supplier/<uuid:supplier_id>/user/add/<str:user_role>/",
        supplier_and_user_management_views.team_member_add_details_view,
        name="add-user-details-select",
    ),
    path(
        "supplier/<uuid:supplier_id>/user/<uuid:user_id>/details/",
        supplier_and_user_management_views.team_member_details_view,
        name="user-details",
    ),
    path(
        "supplier/<uuid:supplier_id>/user/<uuid:user_id>/change-status/",
        supplier_and_user_management_views.team_member_change_status_view,
        name="change-user-status",
    ),
    path(
        "supplier/<uuid:supplier_id>/user/<uuid:user_id>/edit/",
        supplier_and_user_management_views.team_member_edit_view,
        name="edit-user",
    ),
    path("data-download/", download_views.download_csv_view, name="data-download"),
    path("data-download/<uuid:download_id>/", download_views.download_csv_by_id_view, name="download-csv-by-id"),
    path("epc-uploads/", views.epc_page, name="epc-uploads"),
    path("accounts/password-reset/", authentication_views.PasswordReset, name="password-reset"),
    path("accounts/change-password/reset/", authentication_views.PasswordChange, name="password-reset-change"),
    path("accounts/password-reset-done/", authentication_views.password_reset_done, name="password-reset-done"),
    path(
        "accounts/password-reset-from-key-done/",
        authentication_views.password_reset_from_key_done,
        name="password-reset-from-key-done",
    ),
    path(
        "accounts/login/<uuid:user_id>/set-password/<str:token>/",
        authentication_views.SetPassword,
        name="account_login_set_password",
    ),
    path("accept-invite/", authentication_views.AcceptInviteView, name="accept-invite"),
    path("mfa-setup/<uuid:user_id>/<str:token>/", authentication_views.MFASetup, name="mfa-setup"),
    path("user/<uuid:user_id>/verify-otp/<str:token>/", authentication_views.VerifyOTPView, name="verify-otp"),
    path("accounts/login/", authentication_views.CustomLoginView, name="account_login"),
    path("accounts/", include("allauth.urls")),
]

api_patterns = [
    path("healthcheck/", views.healthcheck_view, name="healthcheck"),
]
