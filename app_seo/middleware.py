# app_seo/middleware.py

from .utils import (
    SEOManager,
    set_current_request,
    clear_current_request,
)


# =====================================================
#  نگاشت URL name  →  page_key
# =====================================================

URL_NAME_TO_PAGE_KEY = {

    # app_core
    "home": "home",
    "about": "about",
    "contact": "contact",
    "contact_security": "contact_security",
    "search": "search",
    "error": "404",

    # app_core (انگلیسی)
    "home_en": "home",
    "about_en": "about",
    "contact_en": "contact",
    "contact_security_en": "contact_security",

    # صفحات ثابت دیگر که ممکن است داشته باشی
    # "certificate": "certificate",
    # "vision_missions": "vision_missions",
    # "sustainability": "sustainability",

    # اگر url_name های دیگری داری، اینجا اضافه کن
}


# =====================================================
#  نگاشت url_name  →  (app_label, model_name)
# =====================================================

URL_NAME_TO_MODEL = {

    "product_single": ("app_product", "product"),
    "product_detail": ("app_product", "product"),

    "blog_single": ("app_blog", "blog"),
    "blog_detail": ("app_blog", "blog"),

    "news_single": ("app_news", "news"),
    "news_detail": ("app_news", "news"),

    "media_single": ("app_media", "media"),
    "media_detail": ("app_media", "media"),

    "resume_single": ("app_resume", "resume"),
    "resume_detail": ("app_resume", "resume"),

    # اگر url_name های دیگری داری، اینجا اضافه کن
}


# =====================================================
#  SEOMiddleware
# =====================================================

class SEOMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 1) request را در thread-local بگذار
        set_current_request(request)

        # 2) request.seo را از قبل آماده کن
        request.seo = self._resolve_seo(request)

        try:
            response = self.get_response(request)
        finally:
            # 3) پاک‌سازی thread-local
            clear_current_request()

        return response

    # =================================================
    #  حل SEO برای هر request
    # =================================================

    def _resolve_seo(self, request):

        resolver = getattr(request, "resolver_match", None)

        if not resolver:
            return None

        url_name = resolver.url_name

        # ---------------------------------------------
        # 1) صفحات ثابت  —  با نگاشت صریح
        # ---------------------------------------------

        page_key = URL_NAME_TO_PAGE_KEY.get(url_name)

        if page_key:
            seo = SEOManager.get_page(page_key)

            # اگر SEOSetting در DB وجود داشت، برگردان
            if seo is not None and getattr(seo, "setting", None) is not None:
                return seo

            # حتی اگر تنظیم اختصاصی نبود، SEOContext با default
            # را برگردان (تا تمپلیت‌ها fallback داشته باشند)
            return seo

        # ---------------------------------------------
        # 2) صفحات داینامیک  —  از نگاشت استفاده کن
        # ---------------------------------------------

        model_info = URL_NAME_TO_MODEL.get(url_name)

        if model_info:
            app_label, model_name = model_info
            obj = self._get_object(
                resolver=resolver,
                app_label=app_label,
                model_name=model_name,
            )
            if obj:
                return SEOManager.get_object(obj)

        # ---------------------------------------------
        # 3) fallback  —  تلاش کن خودت مدل را حدس بزنی
        # ---------------------------------------------

        obj = self._guess_object_from_view(resolver)

        if obj:
            return SEOManager.get_object(obj)

        # ---------------------------------------------
        # 4) آخرین تلاش  —  url_name را به‌عنوان page_key
        #    در DB جستجو کن (بدون ساخت SEOContext خالی)
        # ---------------------------------------------

        if url_name:
            from .models import SEOSetting

            exists = (
                SEOSetting.objects
                .filter(
                    content_type="page",
                    page_key=url_name,
                    is_active=True,
                )
                .exists()
            )

            if exists:
                return SEOManager.get_page(url_name)

        return None

    # =================================================
    #  پیدا کردن آبجکت با app_label و model_name
    # =================================================

    def _get_object(self, resolver, app_label, model_name):

        kwargs = resolver.kwargs or {}

        object_id = (
            kwargs.get("pk")
            or kwargs.get("id")
            or kwargs.get("pid")
        )

        slug = (
            kwargs.get("slug")
            or kwargs.get("slug_fa")
            or kwargs.get("slug_en")
        )

        try:
            from django.apps import apps

            model = apps.get_model(app_label, model_name)

            if model is None:
                return None

            if object_id:
                return model.objects.filter(pk=object_id).first()

            if slug:
                for field in ("slug", "slug_fa", "slug_en"):
                    if hasattr(model, field):
                        obj = model.objects.filter(**{field: slug}).first()
                        if obj:
                            return obj

        except Exception:
            return None

        return None

    # =================================================
    #  حدس زدن آبجکت از روی view
    # =================================================

    def _guess_object_from_view(self, resolver):

        kwargs = resolver.kwargs or {}

        object_id = (
            kwargs.get("pk")
            or kwargs.get("id")
            or kwargs.get("pid")
        )

        if not object_id:
            return None

        view_func = resolver.func
        view_class = getattr(view_func, "view_class", None)

        if view_class and hasattr(view_class, "get_queryset"):
            try:
                queryset = view_class.get_queryset()
                return queryset.filter(pk=object_id).first()
            except Exception:
                return None

        return None