
from django.utils.deprecation import MiddlewareMixin

from .utils import (
    SEOManager,
    set_current_request,
    clear_current_request,
)


# =====================================================
# URL name -> page_key
# =====================================================

URL_NAME_TO_PAGE_KEY = {
    # Persian core pages
    "home": "home",
    "about": "about",
    "contact": "contact",
    "contact_security": "contact_security",
    "search": "search",
    "error": "404",

    # English core pages
    "home_en": "home",
    "about_en": "about",
    "contact_en": "contact",
    "contact_security_en": "contact_security",
    "search_en": "search",
}


# =====================================================
# URL name -> (app_label, model_name)
# =====================================================

URL_NAME_TO_MODEL = {
    # Persian
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

    "tender_single": ("app_tender", "tender"),
    "tender_holding_single": ("app_tender_holding", "holding"),
    "auction_single": ("app_auction", "auction"),
    "hr_single": ("app_hr", "jobopportunity"),

    # English
    "product_single_en": ("app_product", "product"),
    "product_detail_en": ("app_product", "product"),

    "blog_single_en": ("app_blog", "blog"),
    "blog_detail_en": ("app_blog", "blog"),

    "news_single_en": ("app_news", "news"),
    "news_detail_en": ("app_news", "news"),

    "media_single_en": ("app_media", "media"),
    "media_detail_en": ("app_media", "media"),

    "resume_single_en": ("app_resume", "resume"),
    "resume_detail_en": ("app_resume", "resume"),

    "tender_single_en": ("app_tender", "tender"),
    "tender_holding_single_en": ("app_tender_holding", "holding"),
    "auction_single_en": ("app_auction", "auction"),
    "hr_single_en": ("app_hr", "jobopportunity"),
}


# =====================================================
# SEO Middleware
# =====================================================

class SEOMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        Store the current request so SEOManager can access it.
        """
        set_current_request(request)
        request.seo = None

    def process_view(
        self,
        request,
        view_func,
        view_args,
        view_kwargs,
    ):
        """
        Django has resolved the URL at this point.
        """
        request.seo = self._resolve_seo(request)
        return None

    def process_response(self, request, response):
        clear_current_request()
        return response

    def process_exception(self, request, exception):
        clear_current_request()
        return None

    # =================================================
    # Resolve SEO for the current page
    # =================================================

    def _resolve_seo(self, request):

        resolver = getattr(request, "resolver_match", None)

        if resolver is None:
            return None

        url_name = resolver.url_name

        # ---------------------------------------------
        # 1. Static pages
        # ---------------------------------------------

        page_key = URL_NAME_TO_PAGE_KEY.get(url_name)

        if page_key:
            return SEOManager.get_page(page_key)

        # ---------------------------------------------
        # 2. Dynamic pages
        # ---------------------------------------------

        model_info = URL_NAME_TO_MODEL.get(url_name)

        if model_info:
            app_label, model_name = model_info

            obj = self._get_object(
                resolver=resolver,
                app_label=app_label,
                model_name=model_name,
            )

            if obj is not None:
                return SEOManager.get_object(obj)

        # ---------------------------------------------
        # 3. Class-based view fallback
        # ---------------------------------------------

        obj = self._guess_object_from_view(resolver)

        if obj is not None:
            return SEOManager.get_object(obj)

        # ---------------------------------------------
        # 4. SEOSetting page_key fallback
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
    # Find a model object
    # =================================================

    def _get_object(
        self,
        resolver,
        app_label,
        model_name,
    ):

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

            model = apps.get_model(
                app_label,
                model_name,
            )

            if model is None:
                return None

            if object_id is not None:
                return (
                    model.objects
                    .filter(pk=object_id)
                    .first()
                )

            if slug:
                model_fields = {
                    field.name
                    for field in model._meta.get_fields()
                }

                for field_name in (
                    "slug",
                    "slug_fa",
                    "slug_en",
                ):
                    if field_name not in model_fields:
                        continue

                    obj = (
                        model.objects
                        .filter(**{field_name: slug})
                        .first()
                    )

                    if obj is not None:
                        return obj

        except Exception:
            return None

        return None

    # =================================================
    # Generic class-based view fallback
    # =================================================

    def _guess_object_from_view(self, resolver):

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

        view_func = resolver.func
        view_class = getattr(
            view_func,
            "view_class",
            None,
        )

        if view_class is None:
            return None

        model = getattr(
            view_class,
            "model",
            None,
        )

        if model is None:
            return None

        try:
            queryset = model._default_manager.all()

            if object_id is not None:
                return queryset.filter(
                    pk=object_id
                ).first()

            if slug:
                model_fields = {
                    field.name
                    for field in model._meta.get_fields()
                }

                for field_name in (
                    "slug",
                    "slug_fa",
                    "slug_en",
                ):
                    if field_name not in model_fields:
                        continue

                    obj = queryset.filter(
                        **{field_name: slug}
                    ).first()

                    if obj is not None:
                        return obj

        except Exception:
            return None

        return None
