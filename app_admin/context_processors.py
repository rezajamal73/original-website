# app_admin/context_processors.py
from app_reports.models import SiteMainInfo  # یا مسیر مدل خود را وارد کنید


def site_logo_context(request):
    """
    دریافت لوگوهای سایت از مدل SiteMainInfo
    """
    try:
        site_info = SiteMainInfo.objects.first()
        if site_info:
            return {
                'SITE_HEADER_LOGO': site_info.header_logo.url if site_info.header_logo else None,
                'SITE_FOOTER_LOGO': site_info.footer_logo.url if site_info.footer_logo else None,
                'SITE_SIDEBAR_LOGO': site_info.sidebar_logo.url if site_info.sidebar_logo else None,
            }
    except:
        pass

    return {
        'SITE_HEADER_LOGO': None,
        'SITE_FOOTER_LOGO': None,
        'SITE_SIDEBAR_LOGO': None,
    }