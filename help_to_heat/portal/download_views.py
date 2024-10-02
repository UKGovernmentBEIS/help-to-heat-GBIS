import codecs
import csv
import io
from datetime import date, datetime, timedelta

import xlsxwriter
from dateutil import tz
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from help_to_heat.frontdoor import models as frontdoor_models
from help_to_heat.frontdoor.consts import (
    epc_details_field,
    property_type_field, recommendations_field,
)
from help_to_heat.frontdoor.eligibility import calculate_eligibility
from help_to_heat.portal import decorators
from help_to_heat.portal import models
from help_to_heat.portal import models as portal_models

london_tz = tz.gettz("Europe/London")

referral_column_headings = (
    "referral_id",
    "ECO4",
    "GBIS",
    "country",
    "first_name",
    "last_name",
    "contact_number",
    "email",
    "own_property",
    "benefits",
    "household_income",
    "uprn",
    "address",
    "postcode",
    "council_tax_band",
    "user_selected_property_type",
    "epc_property_type",
    "property_subtype",
    "property_main_heat_source",
    "epc_rating",
    "accept_suggested_epc",
    "epc_date",
    "number_of_bedrooms",
    "wall_type",
    "wall_insulation",
    "loft",
    "loft_access",
    "loft_insulation",
    "supplier",
    "user_selected_supplier",
    "submission_date",
    "submission_time",
    "lmk_key",
    "address_line_1",
    "address_line_2",
    "address_line_3",
    "post_town",
    "building_reference_number",
    "potential_energy_rating",
    "current_energy_efficiency",
    "potential_energy_efficiency",
    "epc_built_form",
    "inspection_date",
    "local_authority",
    "constituency",
    "county",
    "energy_consumption_current",
    "energy_consumption_potential",
    "co2_emissions_current",
    "co2_emission_current_per_floor_area",
    "co2_emissions_potential",
    "total_floor_area",
    "energy_tariff",
    "mains_gas_flag",
    "floor_level",
    "flat_top_storey",
    "flat_storey_count",
    "main_heating_controls",
    "multi_glaze_proportion",
    "extension_count",
    "number_habitable_rooms",
    "number_heated_rooms",
    "floor_description",
    "floor_energy_efficiency",
    "windows_description",
    "epc_walls_description",
    "walls_energy_efficiency",
    "walls_environmental_efficiency",
    "main_heating_description",
    "main_heating_energy_efficiency",
    "main_heating_environmental_efficiency",
    "secondary_heating_description",
    "secondary_heating_energy_efficiency",
    "secondary_heating_environmental_efficiency",
    "epc_roof_description",
    "roof_energy_efficiency",
    "roof_environmental_efficiency",
    "lighting_description",
    "lighting_energy_efficiency",
    "lighting_environmental_efficiency",
    "main_fuel",
    "floor_height",
    "mechanical_ventilation",
    "construction_age_band",
    "tenure",
    "uprn_source",
    "improvements",
)

referral_column_headings_no_pii = (
    "referral_id",
    "ECO4",
    "GBIS",
    "country",
    "postcode",
    "own_property",
    "benefits",
    "household_income",
    "council_tax_band",
    "user_selected_property_type",
    "epc_property_type",
    "property_subtype",
    "property_main_heat_source",
    "epc_rating",
    "accept_suggested_epc",
    "epc_date",
    "number_of_bedrooms",
    "wall_type",
    "wall_insulation",
    "loft",
    "loft_access",
    "loft_insulation",
    "supplier",
    "user_selected_supplier",
    "submission_date",
    "submission_time",
    "potential_energy_rating",
    "current_energy_efficiency",
    "potential_energy_efficiency",
    "epc_built_form",
    "inspection_date",
    "local_authority",
    "constituency",
    "county",
    "energy_consumption_current",
    "energy_consumption_potential",
    "co2_emissions_current",
    "co2_emission_current_per_floor_area",
    "co2_emissions_potential",
    "total_floor_area",
    "energy_tariff",
    "mains_gas_flag",
    "floor_level",
    "flat_top_storey",
    "flat_storey_count",
    "main_heating_controls",
    "multi_glaze_proportion",
    "extension_count",
    "number_habitable_rooms",
    "number_heated_rooms",
    "floor_description",
    "floor_energy_efficiency",
    "windows_description",
    "epc_walls_description",
    "walls_energy_efficiency",
    "walls_environmental_efficiency",
    "main_heating_description",
    "main_heating_energy_efficiency",
    "main_heating_environmental_efficiency",
    "secondary_heating_description",
    "secondary_heating_energy_efficiency",
    "secondary_heating_environmental_efficiency",
    "epc_roof_description",
    "roof_energy_efficiency",
    "roof_environmental_efficiency",
    "lighting_description",
    "lighting_energy_efficiency",
    "lighting_environmental_efficiency",
    "main_fuel",
    "floor_height",
    "mechanical_ventilation",
    "construction_age_band",
    "tenure",
    "uprn_source",
    "improvements",
)

feedback_column_headings = (
    "page_name",
    "satisfaction_level",
    "service_usage_reason",
    "sufficient_detail_or_guidance",
    "able_to_answer_accurately",
    "received_desired_advice",
    "improvement_comment",
    "submission_date",
    "submission_time",
)


def create_csv(columns, rows, full_file_name):
    headers = {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename={full_file_name}.csv",
    }
    response = HttpResponse(headers=headers, charset="utf-8")
    response.write(codecs.BOM_UTF8)
    writer = csv.DictWriter(response, fieldnames=columns, extrasaction="ignore", dialect=csv.unix_dialect)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return response


def create_referral_csv(referrals, file_name):
    rows = [add_extra_row_data(referral) for referral in referrals]
    full_file_name = f"referral-data-{file_name}"
    response = create_csv(referral_column_headings, rows, full_file_name)
    return response


def create_referral_xlsx(referrals, file_name, exclude_pii=False):
    file_name = file_name + ".xlsx"

    if exclude_pii:
        column_headings = referral_column_headings_no_pii
    else:
        column_headings = referral_column_headings

    # create an in-memory output file for our excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # write the headings
    for col_num, entry in enumerate(column_headings):
        worksheet.write(0, col_num, entry)

    rows = [add_extra_row_data(referral, exclude_pii) for referral in referrals]

    for row_num, referral_data in enumerate(rows):
        for col_num, entry in enumerate(column_headings):
            to_write = referral_data.get(entry) or ""
            worksheet.write(row_num + 1, col_num, to_write)

    workbook.close()

    # rewind to the beginning of the stream before sending our response
    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % file_name

    return response


def handle_create_spreadsheet_request(request, creator):
    referrals = models.Referral.objects.filter(referral_download=None, supplier=request.user.supplier).order_by(
        "referral_id"
    )
    downloaded_at = timezone.now()
    file_name = downloaded_at.strftime("%d-%m-%Y %H_%M")
    new_referral_download = models.ReferralDownload.objects.create(
        created_at=downloaded_at, file_name=file_name, last_downloaded_by=request.user
    )
    response = creator(referrals, file_name)
    new_referral_download.save()
    referrals.update(referral_download=new_referral_download)
    return response


@require_http_methods(["GET"])
@decorators.requires_service_manager
def download_feedback_view(request):
    feedbacks = frontdoor_models.Feedback.objects.all().order_by("created_at")
    downloaded_at = timezone.now()
    file_name = downloaded_at.strftime("%d-%m-%Y %H_%M")
    new_feedback_download = frontdoor_models.FeedbackDownload.objects.create(
        created_at=downloaded_at, file_name=file_name
    )
    response = create_feedback_csv(feedbacks, file_name)
    new_feedback_download.save()
    feedbacks.update(feedback_download=new_feedback_download)
    return response


def create_referral_xlsx_between(start, end, file_name):
    referrals = portal_models.Referral.objects.filter(created_at__gte=start, created_at__lt=end).order_by("referral_id")
    return create_referral_xlsx(referrals, file_name, exclude_pii=True)


@require_http_methods(["GET"])
@decorators.requires_service_manager
def download_referrals_last_week_view(request):
    # Weekly boundaries are Mondays at midnight (00:00)
    # Referrals submitted between Monday 00:00:00 and Sunday 23:59:59 are included
    today = date.today()
    end_of_last_week = today - timedelta(days=today.weekday())
    start_of_last_week = end_of_last_week - timedelta(weeks=1)

    file_name = f"Weekly Referrals ({start_of_last_week.strftime('%d-%m-%Y')})"

    return create_referral_xlsx_between(start_of_last_week, end_of_last_week, file_name)


@require_http_methods(["GET"])
@decorators.requires_service_manager
def download_referrals_range_view(request):
    start_date = datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
    end_date = datetime.strptime(request.GET.get("end"), "%Y-%m-%d")

    formatted_start_date = start_date.strftime("%d-%m-%Y")
    formatted_end_date = end_date.strftime("%d-%m-%Y")
    formatted_date_range = (
        formatted_start_date if start_date == end_date else f"{formatted_start_date} to {formatted_end_date}"
    )
    file_name = f"Referrals ({formatted_date_range})"

    # Date range is inclusive of all referrals made on the end date.
    # e.g. Start: 01 02 2024, End: 06 02 2024 -> All referrals from 01/02/2024 00:00:00 to 06/02/2024 23:59:59
    #      Start: 06 02 2024, End: 06 02 2024 -> All referrals from anytime on that single day (06/02/2024)
    start_of_range = start_date
    end_of_range = end_date + timedelta(days=1)

    return create_referral_xlsx_between(start_of_range, end_of_range, file_name)


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_csv_view(request):
    return handle_create_spreadsheet_request(request, create_referral_csv)


@require_http_methods(["GET"])
@decorators.requires_team_leader_or_member
def download_xlsx_view(request):
    return handle_create_spreadsheet_request(request, create_referral_xlsx)


def handle_create_file_request_by_id(request, download_id, csv_or_xlsx_creator):
    referral_download = models.ReferralDownload.objects.get(pk=download_id)
    if referral_download is None:
        return HttpResponse(status=404)
    referrals = models.Referral.objects.filter(referral_download=referral_download).order_by("referral_id")
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


def add_extra_row_data(referral, exclude_pii=False):
    row = dict(referral.data)
    pii_keys = [
        "first_name",
        "last_name",
        "email",
        "address",
        "contact_number",
    ]

    if exclude_pii:
        for key in pii_keys:
            if key in row.keys():
                row.pop(key)

    eligibility = calculate_eligibility(row)
    epc_date = row.get("epc_date")
    epc_rating = row.get("epc_rating")
    user_selected_property_type = row.get(property_type_field)
    created_at = referral.created_at.astimezone(london_tz)

    if not exclude_pii:
        contact_number = '="' + str(row.get("contact_number", "")) + '"'
        uprn = '="' + str(row.get("uprn", "")) + '"'
        row = {
            **row,
            "contact_number": contact_number,
            "uprn": uprn,
        }

    row = {
        **row,
        "ECO4": "ECO4" in eligibility and "Yes" or "No",
        "GBIS": "GBIS" in eligibility and "Yes" or "No",
        "epc_rating": epc_rating and epc_rating or "",
        "epc_date": epc_date and epc_date or "",
        "submission_date": created_at.date(),
        "submission_time": created_at.time().strftime("%H:%M:%S"),
        "referral_id": referral.formatted_referral_id,
        "user_selected_property_type": user_selected_property_type,
    }

    epc_data = row.get(epc_details_field) or {}

    # add epc data
    row = {
        **row,
        "epc_property_type": epc_data.get("property-type"),
        "potential_energy_rating": epc_data.get("potential-energy-rating"),
        "current_energy_efficiency": epc_data.get("current-energy-efficiency"),
        "potential_energy_efficiency": epc_data.get("potential-energy-efficiency"),
        "epc_built_form": epc_data.get("built-form"),
        "inspection_date": epc_data.get("inspection-date"),
        "local_authority": epc_data.get("local-authority-label"),
        "constituency": epc_data.get("constituency-label"),
        "county": epc_data.get("county"),
        "energy_consumption_current": epc_data.get("energy-consumption-current"),
        "energy_consumption_potential": epc_data.get("energy-consumption-potential"),
        "co2_emissions_current": epc_data.get("co2-emissions-current"),
        "co2_emission_current_per_floor_area": epc_data.get("co2-emiss-curr-per-floor-area"),
        "co2_emissions_potential": epc_data.get("co2-emissions-potential"),
        "total_floor_area": epc_data.get("total-floor-area"),
        "energy_tariff": epc_data.get("energy-tariff"),
        "mains_gas_flag": epc_data.get("mains-gas-flag"),
        "floor_level": epc_data.get("floor-level"),
        "flat_top_storey": epc_data.get("flat-top-storey"),
        "flat_storey_count": epc_data.get("flat-storey-count"),
        "main_heating_controls": epc_data.get("main-heating-controls"),
        "multi_glaze_proportion": epc_data.get("multi-glaze-proportion"),
        "extension_count": epc_data.get("extension-count"),
        "number_habitable_rooms": epc_data.get("number-habitable-rooms"),
        "number_heated_rooms": epc_data.get("number-heated-rooms"),
        "floor_description": epc_data.get("floor-description"),
        "floor_energy_efficiency": epc_data.get("floor-energy-eff"),
        "windows_description": epc_data.get("windows-description"),
        "epc_walls_description": epc_data.get("walls-description"),
        "walls_energy_efficiency": epc_data.get("walls-energy-eff"),
        "walls_environmental_efficiency": epc_data.get("walls-env-eff"),
        "secondary_heating_description": epc_data.get("secondheat-description"),
        "secondary_heating_energy_efficiency": epc_data.get("sheating-energy-eff"),
        "secondary_heating_environmental_efficiency": epc_data.get("sheating-env-eff"),
        "epc_roof_description": epc_data.get("roof-description"),
        "roof_energy_efficiency": epc_data.get("roof-energy-eff"),
        "roof_environmental_efficiency": epc_data.get("roof-env-eff"),
        "main_heating_description": epc_data.get("mainheat-description"),
        "main_heating_energy_efficiency": epc_data.get("mainheat-energy-eff"),
        "main_heating_environmental_efficiency": epc_data.get("mainheat-env-eff"),
        "lighting_description": epc_data.get("lighting-description"),
        "lighting_energy_efficiency": epc_data.get("lighting-energy-eff"),
        "lighting_environmental_efficiency": epc_data.get("lighting-env-eff"),
        "main_fuel": epc_data.get("main-fuel"),
        "floor_height": epc_data.get("floor-height"),
        "mechanical_ventilation": epc_data.get("mechanical-ventilation"),
        "construction_age_band": epc_data.get("construction-age-band"),
        "tenure": epc_data.get("tenure"),
        "uprn_source": epc_data.get("uprn-source"),
    }

    if not exclude_pii:
        row = {
            **row,
            "lmk_key": epc_data.get("lmk-key"),
            "address_line_1": epc_data.get("address1"),
            "address_line_2": epc_data.get("address2"),
            "address_line_3": epc_data.get("address3"),
        }

    # get and concatenate recommendations
    recommendations = row.get(recommendations_field) or []

    recommendations_string = ". ".join(f"{recommendation.get('improvement-item')}: {recommendation.get('improvement-summary-text')}" for recommendation in recommendations)

    row["improvements"] = recommendations_string

    return row


def match_rows_for_feedback(feedback):
    created_at = feedback.created_at.astimezone(london_tz)
    page_name = feedback.page_name
    row = dict(feedback.data)
    row = {
        **row,
        "satisfaction_level": row.get("satisfaction", "Unanswered"),
        "service_usage_reason": row.get("usage-reason", "Unanswered"),
        "sufficient_detail_or_guidance": row.get("guidance", "Unanswered"),
        "able_to_answer_accurately": row.get("accuracy", "Unanswered"),
        "received_desired_advice": row.get("advice", "Unanswered"),
        "improvement_comment": row["more-detail"],
        "page_name": page_name,
        "submission_date": created_at.date(),
        "submission_time": created_at.time().strftime("%H:%M:%S"),
    }
    return row


def create_feedback_csv(feedbacks, file_name):
    rows = [match_rows_for_feedback(feedback) for feedback in feedbacks]
    full_file_name = f"feedback-data-{file_name}"
    response = create_csv(feedback_column_headings, rows, full_file_name)
    return response


@require_http_methods(["GET"])
@decorators.requires_service_manager
def download_all_referrals(_request):
    referrals = models.Referral.objects.all()
    downloaded_at = timezone.now()
    file_name = downloaded_at.strftime("%d-%m-%Y %H_%M")
    response = create_referral_csv(referrals, file_name)
    return response
