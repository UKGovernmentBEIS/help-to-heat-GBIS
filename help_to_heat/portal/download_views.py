import codecs
import csv
import io
import xlsxwriter

from dateutil import tz
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from help_to_heat.frontdoor.eligibility import calculate_eligibility
from help_to_heat.portal import decorators, models

london_tz = tz.gettz("Europe/London")

column_headings = (
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

def create_referral_csv(referrals, file_name):
    headers = {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename=referral-data-{file_name}.csv",
    }
    rows = [add_extra_row_data(referral) for referral in referrals]
    response = HttpResponse(headers=headers, charset="utf-8")
    response.write(codecs.BOM_UTF8)
    writer = csv.DictWriter(response, fieldnames=column_headings, extrasaction="ignore", dialect=csv.unix_dialect)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return response

def create_referral_xlsx(referrals, file_name):
    file_name = file_name + ".xlsx"
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    for col_num, entry in enumerate(column_headings):
        worksheet.write(0, col_num, entry)

    rows = [add_extra_row_data(referral) for referral in referrals]

    for row_num, referral_data in enumerate(rows):
        for col_num, entry in enumerate(column_headings):
            
            to_write = referral_data.get(entry) or ""
            worksheet.write(row_num + 1, col_num, to_write)

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % file_name

    return response


def handle_create_file_request(request, csv_or_xlsx_creator):
    referrals = models.Referral.objects.filter(referral_download=None, supplier=request.user.supplier)
    downloaded_at = timezone.now()
    file_name = downloaded_at.strftime("%d-%m-%Y %H_%M")
    new_referral_download = models.ReferralDownload.objects.create(
        created_at=downloaded_at, file_name=file_name, last_downloaded_by=request.user
    )
    response = csv_or_xlsx_creator(referrals, file_name)
    new_referral_download.save()
    referrals.update(referral_download=new_referral_download)
    return response


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_csv_view(request):
    return handle_create_file_request(request, create_referral_csv)


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_xlsx_view(request):
    return handle_create_file_request(request, create_referral_xlsx)

def handle_create_file_request_by_id(request, download_id, csv_or_xlsx_creator):
    referral_download = models.ReferralDownload.objects.get(pk=download_id)
    if referral_download is None:
        return HttpResponse(status=404)
    referrals = models.Referral.objects.filter(referral_download=referral_download)
    response = create_referral_csv(referrals, referral_download.file_name)
    referral_download.last_downloaded_by = request.user
    referral_download.save()
    return response

@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_csv_by_id_view(request, download_id):
    return handle_create_file_request_by_id(request, download_id, create_referral_csv)

@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_xlsx_by_id_view(request, download_id):
    return handle_create_file_request_by_id(request, download_id, create_referral_xlsx)


def add_extra_row_data(referral):
    row = dict(referral.data)
    eligibility = calculate_eligibility(row)
    epc_date = row.get("epc_date")
    epc_rating = row.get("epc_rating")
    created_at = referral.created_at.astimezone(london_tz)
    contact_number = row.get("contact_number")
    contact_number = '="' + contact_number + '"'
    uprn = row.get("uprn")
    uprn = '="' + str(uprn) + '"' if uprn else ""
    row = {
        **row,
        "contact_number": contact_number,
        "uprn": uprn,
        "ECO4": "Energy Company Obligation 4" in eligibility and "Yes" or "No",
        "GBIS": "Great British Insulation Scheme" in eligibility and "Yes" or "No",
        "epc_rating": epc_rating and epc_rating != "Not found" or "",
        "epc_date": epc_date and epc_date or "",
        "submission_date": created_at.date(),
        "submission_time": created_at.time().strftime("%H:%M:%S"),
    }
    return row