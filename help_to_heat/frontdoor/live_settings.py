from help_to_heat.frontdoor.models import LiveSettings


def public_portal_is_closed():
    return not public_portal_is_open()


def public_portal_is_open():
    live_settings = _get_or_create_live_settings()
    return live_settings.public_portal_open


def set_public_portal_open(open):
    live_settings = _get_or_create_live_settings()
    live_settings.public_portal_open = open
    _save_live_settings(live_settings)


def _get_or_create_live_settings():
    if not LiveSettings.objects.exists():
        live_settings = LiveSettings()
        _save_live_settings(live_settings)
    else:
        live_settings = LiveSettings.objects.first()

    return live_settings


def _save_live_settings(live_settings):
    live_settings.save()
