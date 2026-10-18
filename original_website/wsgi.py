
"""
WSGI configuration for Parsa Novin Kavosh.

Website: https://nkavosh.com

Production environment:
    Django
    SQLite
    cPanel / Passenger

This module exposes the WSGI application
as a module-level variable named application.
"""

import os

from django.core.wsgi import get_wsgi_application


# ==========================================================
# DJANGO SETTINGS
# ==========================================================

# Use production settings by default.
# An explicitly configured environment variable
# takes precedence.

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "original_website.setting.dev",
)


# ==========================================================
# WSGI APPLICATION
# ==========================================================

application = get_wsgi_application()
