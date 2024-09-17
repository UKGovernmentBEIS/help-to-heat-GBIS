import logging

from .settings_base import (
    BASE_DIR,
    SECRET_KEY,
    STATIC_ROOT,
    STATIC_URL,
    STATICFILES_DIRS,
    env,
)

SECRET_KEY = SECRET_KEY
STATIC_URL = STATIC_URL
STATICFILES_DIRS = STATICFILES_DIRS
STATIC_ROOT = STATIC_ROOT

BASE_URL = env.str("BASE_URL")

CONTACT_EMAIL = env.str("CONTACT_EMAIL", default="test@example.com")
FROM_EMAIL = env.str("FROM_EMAIL", default="test@example.com")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

SUPPRESS_COOKIE_BANNER = env.bool("SUPPRESS_COOKIE_BANNER", default=False)
SUPPRESS_LANGUAGE_TOGGLE = env.bool("SUPPRESS_LANGUAGE_TOGGLE", default=False)

# TODO: Replace with fixed hosts once we know the domain
ALLOWED_HOSTS = ["*"]

VCAP_APPLICATION = env.json("VCAP_APPLICATION", default={})

GTAG_ID = env.str("GTAG_ID", default=None)

BASIC_AUTH = env.str("BASIC_AUTH", default="")

# The basic auth parameter cannot be omitted or empty in AWS deployed environments,
# because it is required to be set in the Parameter Store which does not allow blank values.
# For environments that do not use basic auth (e.g. Production),
# we use the special value of "disabled" to indicate that it is not required.
if BASIC_AUTH == "disabled":
    BASIC_AUTH = ""

# Application definition

INSTALLED_APPS = [
    "help_to_heat.portal",
    "help_to_heat.frontdoor",
    "rest_framework",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "debug_toolbar",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

CORS_APPS = [
    "corsheaders",
]

MIDDLEWARE = [
    "help_to_heat.middleware.ExceptionMiddleware",  # at the top to catch all errors that bubble up
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "help_to_heat.middleware.RequestLoggingMiddleware",  # at the bottom to only log requests that aren't blocked
]


# TODO: PC-450 Gross way to check which environment we're in, we should have a var for this
is_developer_environment = BASE_URL == "https://dev.check-eligibility-for-gb-insulation-scheme.service.gov.uk/" or DEBUG


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

if is_developer_environment:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

if BASIC_AUTH:
    MIDDLEWARE = ["help_to_heat.auth.basic_auth_middleware"] + MIDDLEWARE

# Secure transport header timeout 5 minutes; we can up to something larger (like a year) when we're happy it's working.
SECURE_HSTS_SECONDS = 300

# Content Security Policy configurations
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://www.googletagmanager.com/")
CSP_CONNECT_SRC = ("'self'", "*.google-analytics.com/")
CSP_IMG_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

CSRF_COOKIE_HTTPONLY = True

CORS_MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
]

if DEBUG:
    MIDDLEWARE = MIDDLEWARE + CORS_MIDDLEWARE

ROOT_URLCONF = "help_to_heat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            BASE_DIR / "help_to_heat" / "templates",
        ],
        "OPTIONS": {
            "environment": "help_to_heat.jinja2.environment",
            "context_processors": ["help_to_heat.context_processors.add_settings_to_context"],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "help_to_heat" / "templates" / "allauth",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "help_to_heat.context_processors.add_settings_to_context",
            ],
        },
    },
]

WSGI_APPLICATION = "help_to_heat.wsgi.application"

DATABASES = {
    "default": {
        **env.db("DATABASE_URL"),
        **{"ATOMIC_REQUESTS": True},
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "help_to_heat/locale",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "portal.User"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "portal:homepage"
LOGIN_URL = "portal:account_login"
LOGOUT_REDIRECT_URL = "portal:account_login"

EMAIL_BACKEND_TYPE = env.str("EMAIL_BACKEND_TYPE")

if EMAIL_BACKEND_TYPE == "FILE":
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = env.str("EMAIL_FILE_PATH")
elif EMAIL_BACKEND_TYPE == "CONSOLE":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif EMAIL_BACKEND_TYPE == "GOVUKNOTIFY":
    EMAIL_BACKEND = "django_gov_notify.backends.NotifyEmailBackend"
    GOVUK_NOTIFY_API_KEY = env.str("GOVUK_NOTIFY_API_KEY")
    GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID = env.str("GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID")
else:
    if EMAIL_BACKEND_TYPE not in ("FILE", "CONSOLE", "GOVUKNOTIFY"):
        raise Exception(f"Unknown EMAIL_BACKEND_TYPE of {EMAIL_BACKEND_TYPE}")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "help_to_heat": {
            "handlers": ["help_to_heat"],
            "level": "INFO",
            "propagate": False,
        },
        "help_to_heat.requests": {
            "handlers": ["help_to_heat"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {"handlers": ["help_to_heat"], "level": "INFO"},
    },
    "handlers": {
        "help_to_heat": {
            "class": "logging.StreamHandler",
            "formatter": "help_to_heat",
        }
    },
    "formatters": {
        "help_to_heat": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] [{levelname}] {message}",
            "style": "{",
        }
    },
}

OS_API_KEY = env.str("OS_API_KEY")
OPEN_EPC_API_TOKEN = env.str("OPEN_EPC_API_TOKEN")
OPEN_EPC_API_BASE_URL = env.str("OPEN_EPC_API_BASE_URL")

TOTP_ISSUER = "Help to Heat Supplier Portal"

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 60 * 15  # 15 minutes
    SESSION_COOKIE_SAMESITE = "Strict"
    CSRF_COOKIE_SECURE = True

    logging.getLogger("waitress.queue").setLevel(logging.ERROR)
else:
    import debugpy

    try:
        debugpy.listen(("0.0.0.0", 5678))
    except Exception as e:  # noqa: B902
        print("Unable to bind debugpy (if you are running manage.py in local, this is expected):", e)  # noqa: T201
