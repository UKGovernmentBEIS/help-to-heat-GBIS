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

ALLOWED_HOSTS = [
    "help-to-heat-portal-develop.london.cloudapps.digital",
    "help-to-heat-portal-sandbox.london.cloudapps.digital",
    "help-to-heat-portal-staging.london.cloudapps.digital",
    "help-to-heat-portal-suppliers.london.cloudapps.digital",
    "help-to-heat-portal-develop.apps.internal",
    "help-to-heat-portal-sandbox.apps.internal",
    "help-to-heat-portal-staging.apps.internal",
    "help-to-heat-portal-suppliers.apps.internal",
    "help-to-heat-frontdoor-sandbox.london.cloudapps.digital",
    "help-to-heat-frontdoor-develop.london.cloudapps.digital",
    "help-to-heat-frontdoor-staging.london.cloudapps.digital",
    "help-to-heat-frontdoor-suppliers.london.cloudapps.digital",
    "localhost",
    "127.0.0.1",
    "help-to-heat-testserver",
]

VCAP_APPLICATION = env.json("VCAP_APPLICATION", default={})

# Application definition

INSTALLED_APPS = [
    "help_to_heat.portal",
    "rest_framework",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
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
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CSRF settings
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
        "OPTIONS": {"environment": "help_to_heat.jinja2.environment"},
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
    "allauth.account.auth_backends.AuthenticationBackend",
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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "portal.User"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "portal-homepage"
LOGIN_URL = "account_login"

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

SHOW_FRONTDOOR = env.bool("SHOW_FRONTDOOR", default=False)

if SHOW_FRONTDOOR:
    LOGOUT_REDIRECT_URL = "account_login"
