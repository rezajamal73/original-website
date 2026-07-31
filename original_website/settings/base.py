"""
Base Django settings for original_website project.
Shared between development and production.
"""

from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy

# -------------------------------------------------------------
# Base directory
# -------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -------------------------------------------------------------
# Applications
# -------------------------------------------------------------

INSTALLED_APPS = [
    "captcha",
    "jazzmin",

    "adminsortable2",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",

    "django_jalali",

    "app_core.apps.AppBaseConfig",
    "app_banner.apps.AppBannerConfig",
    "app_blog.apps.AppBlogConfig",
    "app_news.apps.AppNewsConfig",
    "app_chart.apps.AppChartConfig",
    "app_product.apps.AppProductConfig",
    "app_tender.apps.AppTenderConfig",
    "app_tender_holding.apps.AppTenderHoldingConfig",
    "app_inquiry.apps.AppInquiryConfig",
    "app_admin",
    "app_auction.apps.AppAuctionConfig",
    "app_security.apps.AppSecurityConfig",
    "app_contact.apps.AppContactConfig",
    "app_reports.apps.AppReportsConfig",
    "app_hr.apps.AppHrConfig",
    "app_media.apps.AppMediaConfig",
    "app_sale.apps.AppSaleConfig",
    "app_catalog.apps.AppCatalogConfig",
    "app_visit.apps.AppVisitConfig",
    "app_resume.apps.AppResumeConfig",
    "app_log.apps.AppLogConfig",
    "app_seo.apps.AppSeoConfig",
    "app_backup.apps.AppBackupConfig",
]

SITE_ID = 2

# -------------------------------------------------------------
# Middleware
# -------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # ثبت بازدید
    "app_visit.middleware.VisitMiddleware",

    "app_log.middleware.CurrentRequestMiddleware",
    "app_seo.middleware.SEOMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

X_FRAME_OPTIONS = "SAMEORIGIN"

ROOT_URLCONF = "original_website.urls"

# -------------------------------------------------------------
# Templates
# -------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app_seo.context_processors.seo",
                "app_core.context_processors.common_context",
            ],
        },
    },
]

WSGI_APPLICATION = "original_website.wsgi.application"

# -------------------------------------------------------------
# Database
# -------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------------
# Password validation
# -------------------------------------------------------------

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

# -------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------

LANGUAGE_CODE = "fa"

LANGUAGES = [
    ("fa", "فارسی"),
]

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True

# -------------------------------------------------------------
# Static & Media
# -------------------------------------------------------------

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    BASE_DIR / "statics",
]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------
# Captcha
# -------------------------------------------------------------

# تعداد کاراکترها
CAPTCHA_LENGTH = 5

# اعتبار (دقیقه)
CAPTCHA_TIMEOUT = 5

# اندازه تصویر
CAPTCHA_IMAGE_SIZE = (220, 70)

# اندازه فونت
CAPTCHA_FONT_SIZE = 34

# چرخش کم برای خوانایی بیشتر
CAPTCHA_LETTER_ROTATION = (-8, 8)

# فقط نویز نقطه‌ای
CAPTCHA_NOISE_FUNCTIONS = (
    "captcha.helpers.noise_dots",
)

# بدون فیلتر اضافی
CAPTCHA_FILTER_FUNCTIONS = ()

# رنگ‌ها
CAPTCHA_BACKGROUND_COLOR = "#ffffff"
CAPTCHA_FOREGROUND_COLOR = "#111111"

# =============================================================
# Jazzmin Settings
# =============================================================

JAZZMIN_SETTINGS = {

    # ---------------------------------------------------------
    # Branding
    # ---------------------------------------------------------

    "site_title": "پنل مدیریت پیشرفته",
    "site_header": "پنل مدیریت",
    "site_brand": "داشبورد مدیریت",
    "welcome_sign": "👋",
    "copyright": "RJ ۱۴۰۵ - تمامی حقوق محفوظ است",

    "site_logo": "admin-custom/images/logos/logo.png",
    "login_logo": "admin-custom/images/logos/logo.png",
    "login_logo_dark": "admin-custom/images/logos/logo.png",
    "site_icon": "admin-custom/images/logos/favicon.ico",

    # ---------------------------------------------------------
    # Top Menu
    # ---------------------------------------------------------

    "topmenu_links": [

        {
            "name": "🏠 مشاهده سایت",
            "url": "/",
            "new_window": True,
        },

        {
            "app": "app_catalog",
            "label": "📚 کاتالوگ",
        },

        {
            "app": "app_banner",
            "label": "🎨 بنرها",
        },

        {
            "app": "app_resume",
            "label": "📁 رزومه",
        },

        {
            "app": "app_seo",
            "label": "🔍 سئو",
        },

        {
            "app": "app_backup",
            "label": "💾 پشتیبان‌گیری",
        },

        {
            "app": "app_log",
            "label": "📜 لاگ سیستم",
        },
    ],

    # ---------------------------------------------------------
    # Sidebar
    # ---------------------------------------------------------

    "show_sidebar": True,
    "navigation_expanded": False,

    "hide_apps": [
        "app_news",
        "app_tender",
        "app_auction",
        "app_inquiry",
        "app_security",
        "app_catalog",
        "app_tender_holding",
        "app_hr",
        "app_sale",
    ],

    "hide_models": [
        "app_reports.GroupCompany",
        "app_reports.DepartmentContact",
        "app_chart.BoardMember",
    ],

    # ---------------------------------------------------------
    # Order
    # ---------------------------------------------------------

    "order_with_respect_to": [

        # فروش و محصولات
        "app_product",
        "app_product.Product",
        "app_product.ProductCategory",
        "app_product.ProductCategory2",
        "app_product.ProductTag",

        # محتوا
        "app_blog",
        "app_blog.blog",
        "app_blog.blog_Category",
        "app_blog.blog_Tag",

        "app_news",
        "app_news.News",
        "app_news.NewsCategory",
        "app_news.NewsTag",

        "app_media",
        "app_media.Media",

        # مناقصه
        "app_tender",
        "app_tender.Tender",
        "app_tender.TenderCategory",

        "app_tender_holding",
        "app_tender_holding.Holding",

        "app_auction",
        "app_auction.Auction",

        # استعلام
        "app_inquiry",
        "app_inquiry.PurchaseInquiry",

        "app_sale",
        "app_sale.SalesReport",

        # سازمان
        "app_chart",
        "app_chart.Person",
        "app_chart.BoardMember",

        "app_hr",
        "app_hr.JobOpportunity",
        "app_hr.JobApplication",

        # ارتباطات
        "app_contact",
        "app_contact.ContactMessage",

        "app_security",
        "app_security.SecurityContact",

        # کاتالوگ
        "app_catalog",
        "app_catalog.CompanyCatalog",

        # بنر
        "app_banner",
        "app_banner.HeroSliderSetting",
        "app_banner.HeroBanner",
        "app_banner.MainBanner",
        "app_banner.OtherBanner",
        "app_banner.SpecialProductBanner",

        # اطلاعات شرکت
        "app_reports",
        "app_reports.SiteMainInfo",
        "app_reports.CorporateSection",
        "app_reports.CorporateStatistic",
        "app_reports.GroupCompany",
        "app_reports.DepartmentContact",
        "app_reports.FollowUsLink",
        "app_reports.Project",
        "app_reports.CorporateText",

        # رزومه
        "app_resume",
        "app_resume.Resume",
        "app_resume.ResumeProvince",

        # بازدید
        "app_visit",
        "app_visit.Visit",

        # سئو
        "app_seo",
        "app_seo.SEOSetting",

        # لاگ
        "app_log",
        "app_log.SystemLog",

        # بکاپ
        "app_backup",
        "app_backup.Backup",

        # Sites
        "django.contrib.sites",
        "sites",
        "sites.Site",

        # Admin
        "admin",
        "admin.LogEntry",

        # Users
        "app_core",
        "app_core.UserProxy",
        "app_core.GroupProxy",
    ],

    # ---------------------------------------------------------
    # Icons
    # ---------------------------------------------------------

    "icons": {

        "app_product": "",
        "app_product.Product": "fas fa-box-open",
        "app_product.ProductCategory": "fas fa-folder",
        "app_product.ProductCategory2": "fas fa-folder-tree",
        "app_product.ProductTag": "fas fa-tags",

        "app_blog": "",
        "app_blog.blog": "fas fa-pen-nib",
        "app_blog.blog_Category": "fas fa-folder",
        "app_blog.blog_Tag": "fas fa-tags",

        "app_news": "",
        "app_news.News": "fas fa-newspaper",
        "app_news.NewsCategory": "fas fa-folder-open",
        "app_news.NewsTag": "fas fa-tags",

        "app_media": "",
        "app_media.Media": "fas fa-photo-video",

        "app_tender": "",
        "app_tender.Tender": "fas fa-file-contract",
        "app_tender.TenderCategory": "fas fa-folder",

        "app_tender_holding": "",
        "app_tender_holding.Holding": "fas fa-building",

        "app_auction": "",
        "app_auction.Auction": "fas fa-gavel",

        "app_inquiry": "",
        "app_inquiry.PurchaseInquiry": "fas fa-file-invoice-dollar",

        "app_sale": "",
        "app_sale.SalesReport": "fas fa-chart-line",

        "app_chart": "",
        "app_chart.Person": "fas fa-user-tie",
        "app_chart.BoardMember": "fas fa-user-shield",

        "app_hr": "",
        "app_hr.JobOpportunity": "fas fa-briefcase",
        "app_hr.JobApplication": "fas fa-file-signature",

        "app_contact": "",
        "app_contact.ContactMessage": "fas fa-envelope-open-text",

        "app_security": "",
        "app_security.SecurityContact": "fas fa-shield-alt",

        "app_catalog": "",
        "app_catalog.CompanyCatalog": "fas fa-book",

        "app_banner": "",
        "app_banner.HeroSliderSetting": "fas fa-sliders-h",
        "app_banner.HeroBanner": "fas fa-desktop",
        "app_banner.MainBanner": "fas fa-flag",
        "app_banner.OtherBanner": "fas fa-image",
        "app_banner.SpecialProductBanner": "fas fa-star",

        "app_reports": "",
        "app_reports.SiteMainInfo": "fas fa-info-circle",
        "app_reports.CorporateSection": "fas fa-layer-group",
        "app_reports.CorporateStatistic": "fas fa-chart-pie",
        "app_reports.GroupCompany": "fas fa-city",
        "app_reports.DepartmentContact": "fas fa-phone-alt",
        "app_reports.FollowUsLink": "fas fa-link",
        "app_reports.CorporateText": "fas fa-align-left",
        "app_reports.Project": "fas fa-project-diagram",

        "app_visit": "",
        "app_visit.Visit": "fas fa-eye",

        "app_resume": "",
        "app_resume.Resume": "fas fa-file-alt",
        "app_resume.ResumeProvince": "fas fa-map-marker-alt",

        "app_seo": "",
        "app_seo.SEOSetting": "fas fa-search",

        "app_log": "",
        "app_log.SystemLog": "fas fa-history",

        "app_backup": "",
        "app_backup.Backup": "fas fa-database",

        "sites": "",
        "sites.Site": "fas fa-globe",

        "admin": "",
        "admin.LogEntry": "fas fa-cogs",

        "app_core": "",
        "app_core.UserProxy": "fas fa-user",
        "app_core.GroupProxy": "fas fa-user-friends",
    },

    # ---------------------------------------------------------
    # Default Icons
    # ---------------------------------------------------------

    "default_icon_parents": "fas fa-folder-open",
    "default_icon_children": "fas fa-circle",

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    "related_modal_active": True,
    "custom_css": "admin-custom/css/admin-custom.css",
    "custom_js": "admin-custom/js/admin-custom.js",

    "use_google_fonts_cdn": False,
    "show_ui_builder": False,

    "changeform_format": "horizontal_tabs",

    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "collapsible",
    },

    "language_chooser": False,
}

# =============================================================
# Jazzmin UI Tweaks
# =============================================================

JAZZMIN_UI_TWEAKS = {

    # ---------------------------------------------------------
    # Theme
    # ---------------------------------------------------------

    "theme": "flatly",
    "dark_mode_theme": "darkly",

    # ---------------------------------------------------------
    # Colors
    # ---------------------------------------------------------

    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",

    # ---------------------------------------------------------
    # Font Size
    # ---------------------------------------------------------

    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "sidebar_nav_small_text": False,

    # ---------------------------------------------------------
    # Navbar
    # ---------------------------------------------------------

    "navbar_fixed": True,
    "no_navbar_border": True,

    # ---------------------------------------------------------
    # Sidebar
    # ---------------------------------------------------------

    "sidebar_fixed": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "sidebar_disable_expand": False,

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    "footer_fixed": False,

    # ---------------------------------------------------------
    # Layout
    # ---------------------------------------------------------

    "layout_boxed": False,

    # ---------------------------------------------------------
    # Buttons
    # ---------------------------------------------------------

    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },

    # ---------------------------------------------------------
    # Extra
    # ---------------------------------------------------------

    "actions_sticky_top": True,
}

# =============================================================
# Global Search
# =============================================================

JAZZMIN_SETTINGS["global_search"] = [
    "app_product.Product",
    "app_blog.blog",
    "app_news.News",
    "auth.User",
]