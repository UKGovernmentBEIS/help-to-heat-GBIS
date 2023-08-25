from django.conf import settings


def add_settings_to_context(request):
    return {
        "DEBUG": settings.DEBUG,
        "SUPPRESS_COOKIE_BANNER": settings.SUPPRESS_COOKIE_BANNER,
        "SUPPRESS_LANGUAGE_TOGGLE": settings.SUPPRESS_LANGUAGE_TOGGLE,
        "space_name": settings.VCAP_APPLICATION.get("space_name", "unknown"),
    }
