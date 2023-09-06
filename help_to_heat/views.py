import os

from django.http import HttpResponse
from django.shortcuts import render

from help_to_heat import settings


def robots_txt_view(request):
    file_path = os.path.join(settings.BASE_DIR, "static/robots.txt")
    with open(file_path, "r") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/plain")


def digital_assistance_view(request):
    # next_url = "https://www.gov.uk/apply-great-british-insulation-scheme"
    # response = render(next_url)
    # response.set_cookie("digital_assistance", True)

    return render(request, template_name="digitalassistance.html", context={})
