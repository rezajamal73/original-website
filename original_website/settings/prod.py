from .base import *
import os

# =============================================================
# Production Settings
# =============================================================

# SECRET KEY
# بهتر است از متغیر محیطی یا فایل .env خوانده شود
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Debug
DEBUG = False

# دامنه‌های مجاز
ALLOWED_HOSTS = [
    "nkavosh.com",
    "www.nkavosh.com",
]

# -------------------------------------------------------------
# Security
# -------------------------------------------------------------

# فقط HTTPS
SECURE_SSL_REDIRECT = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Browser Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Clickjacking
X_FRAME_OPTIONS = "DENY"

# Referrer Policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# -------------------------------------------------------------
# Email
# -------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"