import csv

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from help_to_heat.frontdoor.eligibility import calculate_eligibility
from help_to_heat.portal import decorators, models

csv_columns = (
    "ECO4",
    "GBIS",
    "first_name",
    "last_name",
    "contact_number",
    "email",
    "own_property",
    "benefits",
    "household_income",
    "uprn",
    "address_line_1",
    "postcode",
    "address",
    "council_tax_band",
    "property_type",
    "property_subtype",
    "epc_rating",
    "accept_suggested_epc",
    "epc_date",
    "number_of_bedrooms",
    "wall_type",
    "wall_insulation",
    "loft",
    "loft_access",
    "loft_insulation",
    "Property main heat source",
    "supplier",
    "submission_date",
    "submission_time",
)


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_csv_view(request):
    referrals = models.Referral.objects.filter(referral_download=None, supplier=request.user.supplier)
    downloaded_at = timezone.now()
    file_name = downloaded_at.strftime("%d-%m-%Y %H_%M")
    new_referral_download = models.ReferralDownload.objects.create(
        created_at=downloaded_at, file_name=file_name, last_downloaded_by=request.user
    )
    response = create_referral_csv(referrals, file_name)
    new_referral_download.save()
    referrals.update(referral_download=new_referral_download)
    return response


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_csv_by_id_view(request, download_id):
    referral_download = models.ReferralDownload.objects.get(pk=download_id)
    if referral_download is None:
        return HttpResponse(status=404)
    referrals = models.Referral.objects.filter(referral_download=referral_download)
    response = create_referral_csv(referrals, referral_download.file_name)
    referral_download.last_downloaded_by = request.user
    referral_download.save()
    return response


def add_extra_row_data(referral):
    row = dict(referral.data)
    eligibility = calculate_eligibility(row)
    epc_date = row.get("epc_date")
    row = {
        **row,
        "ECO4": "Energy Company Obligation 4" in eligibility and "Yes" or "No",
        "GBIS": "Great British Insulation Scheme" in eligibility and "Yes" or "No",
        "epc_date": epc_date and epc_date or "Not found",
        "submission_date": referral.created_at.date(),
        "submission_time": referral.created_at.time().strftime("%H:%M:%S'"),
    }
    return row


def create_referral_csv(referrals, file_name):
    headers = {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename=referral-data-{file_name}.csv",
    }
    rows = [add_extra_row_data(referral) for referral in referrals]
    response = HttpResponse(headers=headers)
    writer = csv.DictWriter(response, fieldnames=csv_columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return response
