import os

from django.http import HttpResponse
from django.shortcuts import render

from help_to_heat import settings
from help_to_heat.frontdoor.consts import govuk_start_page_url


def robots_txt_view(request):
    file_path = os.path.join(settings.BASE_DIR, "static/robots.txt")
    with open(file_path, "r") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/plain")


def digital_assistance_view(request):
    return render(
        request, template_name="frontdoor/digitalassistance.html", context={"govuk_url": govuk_start_page_url}
    )
