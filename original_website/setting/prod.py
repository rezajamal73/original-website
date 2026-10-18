
"""
Production settings for nkavosh.com

Django + SQLite + cPanel + Passenger
"""

import os
import stat
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

from original_website.settings import *


# ==========================================================
# ENVIRONMENT
# ==========================================================

DEBUG = False

ALLOWED_HOSTS = [
    "nkavosh.com",
    "www.nkavosh.com",
]

SITE_URL = "https://nkavosh.com"
SITE_ID = 2


# ==========================================================
# SECRET KEY
# ==========================================================

SECRET_FILE = Path.home() / ".nkavosh_django_secret"

environment_secret = os.environ.get(
    "DJANGO_SECRET_KEY", ""
).strip()

if environment_secret:
    SECRET_KEY = environment_secret
else:
    try:
        fd = os.open(
            str(SECRET_FILE),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        pass
    else:
        with os.fdopen(fd, "w", encoding="utf-8") as secret_file:
            secret_file.write(get_random_secret_key())

    SECRET_KEY = SECRET_FILE.read_text(
        encoding="utf-8"
    ).strip()

    try:
        SECRET_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Production SECRET_KEY is missing."
    )


# ==========================================================
# PATHS
# ==========================================================

PUBLIC_HTML = Path("/home/nkavoshc/public_html")


# ==========================================================
# DATABASE
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 30,
        },
    }
}


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = "/static/"
STATIC_ROOT = PUBLIC_HTML / "static"

STATICFILES_DIRS = [
    BASE_DIR / "statics",
]


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = PUBLIC_HTML / "media"


# ==========================================================
# HTTPS AND COOKIES
# ==========================================================

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_TRUSTED_ORIGINS = [
    "https://nkavosh.com",
    "https://www.nkavosh.com",
]

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None


# ==========================================================
# HSTS
# ==========================================================

SECURE_HSTS_SECONDS = 300
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# ==========================================================
# BROWSER SECURITY
# ==========================================================

X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = (
    "strict-origin-when-cross-origin"
)


# ==========================================================
# SESSION
# ==========================================================

SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False


# ==========================================================
# FILE UPLOAD LIMITS
# ==========================================================

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000


# ==========================================================
# VISITOR IP
# ==========================================================

VISIT_TRUSTED_PROXIES = ()


# ==========================================================
# LANGUAGE AND TIMEZONE
# ==========================================================

LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"

USE_I18N = True
USE_TZ = True


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================================
# DJANGO AXES - LOGIN PROTECTION
# ==========================================================


AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AXES_ENABLED = True

AXES_FAILURE_LIMIT = 15

AXES_COOLOFF_TIME = timedelta(minutes=15)

AXES_IPWARE_META_PRECEDENCE_ORDER = (
    "REMOTE_ADDR",
)

AXES_LOCKOUT_PARAMETERS = [
    "ip_address",
]

AXES_RESET_ON_SUCCESS = True

AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False

AXES_LOCKOUT_CALLABLE = (
    "app_admin.security_middleware.axes_lockout_response"
)


# ==========================================================
# LOGGING
# ==========================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s "
                "[%(levelname)s] "
                "%(name)s: %(message)s"
            ),
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "WARNING",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },

        "app_backup": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },

        "app_visit": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


# ==========================================================
# ADMIN IP SECURITY
# ==========================================================

# Keep existing explicit IP blocks active.
ADMIN_IP_BLOCKING_ENABLED = True

# IMPORTANT:
# Start with False.
# Enable only after your own public IP is registered
# and verified in the allowed IP list.
ADMIN_IP_ALLOWLIST_ENABLED = False

MIDDLEWARE = [
    "app_admin.security_middleware.AdminIPSecurityMiddleware",
    *MIDDLEWARE,
]


# ==========================================================
# JAZZMIN - ALLOWED IP MENU
# ==========================================================

# Preserve the existing Jazzmin menu and insert the
# new item immediately after SecurityIPRule.

_security_menu_order = JAZZMIN_SETTINGS.get(
    "order_with_respect_to",
    [],
)

if (
    "app_admin.SecurityIPRule" in _security_menu_order
    and "app_admin.AllowedIP" not in _security_menu_order
):
    _security_menu_order.insert(
        _security_menu_order.index(
            "app_admin.SecurityIPRule"
        ) + 1,
        "app_admin.AllowedIP",
    )

JAZZMIN_SETTINGS.setdefault(
    "icons",
    {},
)["app_admin.AllowedIP"] = "fas fa-user-shield"
