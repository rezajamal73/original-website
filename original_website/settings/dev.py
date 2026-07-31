from .base import *

# =============================================================
# Development Settings
# =============================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gs9k^w59&yy8$%+^g8q=%0d@3fhsn3=y6u&p_p^k$=o3&ir(2$"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# -------------------------------------------------------------
# Security (Development)
# -------------------------------------------------------------

SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

X_FRAME_OPTIONS = "SAMEORIGIN"

# -------------------------------------------------------------
# Email
# -------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"