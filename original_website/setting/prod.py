
from original_website.settings import *
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import os

# ------------------------------------------------------------------
# SECURITY — Automatic persistent SECRET_KEY
# کلید فقط یک بار ساخته می‌شود و در اجراهای بعدی ثابت می‌ماند.

SECRET_FILE = Path.home() / ".nkavosh_django_secret"

try:
    fd = os.open(
        str(SECRET_FILE),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600
    )
except FileExistsError:
    pass
else:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(get_random_secret_key())

SECRET_KEY = SECRET_FILE.read_text(encoding="utf-8").strip()

if not SECRET_KEY:
    raise RuntimeError("Django SECRET_KEY file is empty.")

# ------------------------------------------------------------------
# PRODUCTION

DEBUG = False

ALLOWED_HOSTS = ['nkavosh.com', 'www.nkavosh.com']

SITE_ID = 2

# ------------------------------------------------------------------
# مسیر public_html روی هاست
PUBLIC_HTML = Path('/home/nkavoshc/public_html')

# ------------------------------------------------------------------
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------------------------
# STATIC
STATIC_URL = '/static/'
STATIC_ROOT = PUBLIC_HTML / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'statics',
]

# ------------------------------------------------------------------
# MEDIA — مستقیم تو public_html/media
MEDIA_URL = '/media/'
MEDIA_ROOT = PUBLIC_HTML / 'media'

# ------------------------------------------------------------------
# SECURITY
CSRF_COOKIE_SECURE = True
