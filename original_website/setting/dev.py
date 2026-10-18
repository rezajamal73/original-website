
from original_website.settings import *
from pathlib import Path

# ==========================================================
# DEVELOPMENT ENVIRONMENT
# ==========================================================

SECRET_KEY = (
    "django-insecure-"
    "gs9k^w59&yy8$%+^g8q=%0d@3fhsn3=y6u&p_p^k$=o3&ir(2$"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

SITE_ID = 2

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
MEDIA_ROOT = BASE_DIR / "media"

# ==========================================================
# BROWSER SECURITY
# ==========================================================

X_FRAME_OPTIONS = "SAMEORIGIN"

# ==========================================================
# ADMIN IP SECURITY - DEVELOPMENT
# ==========================================================

ADMIN_IP_BLOCKING_ENABLED = False
ADMIN_IP_ALLOWLIST_ENABLED = False
