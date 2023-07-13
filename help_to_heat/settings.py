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

# TODO: Replace with fixed hosts once we know the domain
ALLOWED_HOSTS = ["*"]

VCAP_APPLICATION = env.json("VCAP_APPLICATION", default={})

GTAG_ID = env.str("GTAG_ID", default=None)
BASIC_AUTH = env.str("BASIC_AUTH", default="")

# Application definition

INSTALLED_APPS = [
    "help_to_heat.portal",
    "help_to_heat.frontdoor",
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

if BASIC_AUTH:
    MIDDLEWARE = ["help_to_heat.auth.basic_auth_middleware"] + MIDDLEWARE

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

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

OS_API_KEY = env.str("OS_API_KEY")

TOTP_ISSUER = "Help to Heat Supplier Portal"

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 60 * 10  # 10 minutes
    SESSION_COOKIE_SAMESITE = "Strict"
else:
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
