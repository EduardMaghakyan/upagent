import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compressor",
    "django.contrib.sites",
    "django_rq",
    "monitors",
    "status_page",
    "authentication",
]

SITE_ID = 1


LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "monitor_list"
LOGOUT_REDIRECT_URL = "login"


EMAIL_BACKEND = "postmarker.django.backend.EmailBackend"

POSTMARK_TOKEN = os.environ.get("POSTMARK_SERVER_TOKEN", "")
POSTMARK_SENDER = os.environ.get("POSTMARK_SENDER", "noreply@aassit.ai")
DEFAULT_FROM_EMAIL = POSTMARK_SENDER

if not POSTMARK_TOKEN:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    print("WARNING: Postmark API key not set, emails will be sent to console")


POSTMARK = {
    "TOKEN": POSTMARK_TOKEN,
    "SENDER": POSTMARK_SENDER,
}

RATELIMIT_VIEW = "authentication.views.ratelimit_view"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
    "authentication.middleware.TwoFactorMiddleware",
]

ROOT_URLCONF = "upagent_monitor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),  # Project-wide templates
        ],
        "APP_DIRS": True,  # This enables Django to find templates in app directories
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "authentication.context_processors.email_context",
            ],
        },
    },
]

WSGI_APPLICATION = "upagent_monitor.wsgi.application"

# Database
if DATABASE_URL := os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/staticfiles/"
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "upagent_monitor.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "monitors": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}


if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Compressor settings
COMPRESS_ROOT = BASE_DIR / "static"
COMPRESS_ENABLED = True
STATICFILES_FINDERS = ("compressor.finders.CompressorFinder",)


# Email context variables
SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "support@yourdomain.com")
COMPANY_NAME = os.environ.get("COMPANY_NAME", "Your Company")
COMPANY_ADDRESS = os.environ.get("COMPANY_ADDRESS", "")
UNSUBSCRIBE_URL = os.environ.get("UNSUBSCRIBE_URL", "#")

# Session settings for 2FA
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Use database-backed sessions
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_SECURE = not DEBUG  # True in production

# Two-factor authentication settings
TWO_FACTOR_EMAIL_OTP_EXPIRY_MINUTES = 10  # OTP expiry time in minutes


# RQ settings
RQ_QUEUES = {
    "default": {
        "URL": os.environ.get("RQ_REDIS_URL", "redis://redis:6379/0"),
        "DEFAULT_TIMEOUT": 360,
    },
    "high": {
        "URL": os.environ.get("RQ_REDIS_URL", "redis://redis:6379/0"),
        "DEFAULT_TIMEOUT": 360,
    },
    "low": {
        "URL": os.environ.get("RQ_REDIS_URL", "redis://redis:6379/0"),
        "DEFAULT_TIMEOUT": 360,
    },
}

# If you want to use password for Redis
# RQ_QUEUES = {
#     'default': {
#         'HOST': 'localhost',
#         'PORT': 6379,
#         'DB': 0,
#         'PASSWORD': 'your-password',
#         'DEFAULT_TIMEOUT': 360,
#     },
#     # ... other queues
# }

RQ_SCHEDULER_QUEUE = "default"
