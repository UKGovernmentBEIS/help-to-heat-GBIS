from django.conf import settings
import os


def add_settings_to_context(request):
    return {
        "DEBUG": settings.DEBUG,
        "space_name": settings.VCAP_APPLICATION.get("space_name", "unknown"),
    }


def suppress_cookie_banner(request):
    suppress_cookie_banner_value = os.environ.get('SUPPRESS_COOKIE_BANNER', False)
    return {'SUPPRESS_COOKIE_BANNER': suppress_cookie_banner_value}
