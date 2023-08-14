from django.conf import settings


def add_settings_to_context(request):
    return {
        "DEBUG": settings.DEBUG,
        "SUPPRESS_COOKIE_BANNER": settings.SUPPRESS_COOKIE_BANNER,
        "space_name": settings.VCAP_APPLICATION.get("space_name", "unknown"),
    }
