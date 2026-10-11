from original_website.settings import *
from pathlib import Path

# Quick-start development setting - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gs9k^w59&yy8$%+^g8q=%0d@3fhsn3=y6u&p_p^k$=o3&ir(2$'

# SECURITY WARNING: don't run with debug turned on in production!
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
STATIC_URL  = '/static/'
STATIC_ROOT = PUBLIC_HTML / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'statics',
]

# ------------------------------------------------------------------
# MEDIA — مستقیم تو public_html/media
MEDIA_URL  = '/media/'
MEDIA_ROOT = PUBLIC_HTML / 'media'

# ------------------------------------------------------------------
# SECURITY
CSRF_COOKIE_SECURE = True