# app_seo/utils.py

import json
import threading

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static

from .models import SEOSetting, SEODefault


# =====================================================
#  Thread-local storage
# =====================================================

_thread_locals = threading.local()


def set_current_request(request):
    _thread_locals.request = request


def get_current_request():
    return getattr(_thread_locals, "request", None)


def clear_current_request():
    if hasattr(_thread_locals, "request"):
        del _thread_locals.request


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _detect_language(request):
    if request is None:
        return "fa"
    path = getattr(request, "path", "") or ""
    if path.startswith("/en/"):
        return "en"
    return "fa"


def _build_absolute(request, path_or_url):
    if not path_or_url:
        return ""
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    if request is None:
        return path_or_url
    try:
        return request.build_absolute_uri(path_or_url)
    except Exception:
        return path_or_url


def _default_og_image_url():
    try:
        return static("images/default-og.jpg")
    except Exception:
        return ""


def _site_base_url():
    return getattr(settings, "SITE_URL", "").rstrip("/")


# =====================================================
#  SEOContext
# =====================================================

class SEOContext:

    def __init__(
        self,
        setting=None,
        default=None,
        obj=None,
        page_key=None,
        content_type=None,
        request=None,
    ):
        self.setting = setting
        self.default = default
        self.obj = obj
        self.page_key = page_key
        self.content_type = (
            content_type
            or (setting.content_type if setting else None)
            or "page"
        )
        self.request = request
        self._cache = {}

    # ------- helper -------

    def _pick(self, *values):
        for v in values:
            if v is None:
                continue
            if isinstance(v, str) and not v.strip():
                continue
            return v
        return None

    # =====================
    #  پایه
    # =====================

    @property
    def title(self):
        value = self._pick(
            getattr(self.setting, "title", None) if self.setting else None,
            getattr(self.obj, "title_fa", None) if self.obj else None,
            getattr(self.obj, "title_en", None) if self.obj else None,
            getattr(self.obj, "title", None) if self.obj else None,
        )
        return value or ""

    @property
    def description(self):
        return self._pick(
            getattr(self.setting, "description", None) if self.setting else None,
            getattr(self.obj, "description_fa", None) if self.obj else None,
            getattr(self.obj, "description_en", None) if self.obj else None,
            getattr(self.obj, "description", None) if self.obj else None,
        ) or ""

    @property
    def keywords(self):
        return self._pick(
            getattr(self.setting, "keywords", None) if self.setting else None,
        ) or ""

    @property
    def canonical(self):
        manual = getattr(self.setting, "canonical", None) if self.setting else None
        if manual:
            return manual

        if self.request is not None:
            try:
                return self.request.build_absolute_uri(self.request.path)
            except Exception:
                pass

        manual_url = getattr(self.setting, "url", None) if self.setting else None
        if manual_url:
            return manual_url

        return ""

    # =====================
    #  Robots
    # =====================

    @property
    def robots(self):
        page_key = self.page_key or ""

        if page_key in ("404", "search"):
            return "noindex,nofollow"

        if self.setting is not None:
            index_control = getattr(self.setting, "index_control", None)
            follow_control = getattr(self.setting, "follow_control", None)

            if index_control and follow_control:
                return f"{index_control},{follow_control}"

            legacy = getattr(self.setting, "robots", None)
            if legacy:
                return legacy

        return "index,follow"

    @property
    def index_control(self):
        return self.robots.split(",")[0].strip() or "index"

    @property
    def follow_control(self):
        parts = self.robots.split(",")
        return parts[1].strip() if len(parts) > 1 else "follow"

    # =====================
    #  Open Graph
    # =====================

    @property
    def og_title(self):
        return self._pick(
            getattr(self.setting, "og_title", None) if self.setting else None,
            self.title,
        ) or ""

    @property
    def og_description(self):
        return self._pick(
            getattr(self.setting, "og_description", None) if self.setting else None,
            self.description,
        ) or ""

    @property
    def og_type(self):
        return self._pick(
            getattr(self.setting, "og_type", None) if self.setting else None,
        ) or "website"

    @property
    def og_image(self):
        if "og_image" in self._cache:
            return self._cache["og_image"]

        image = None

        if self.setting is not None and getattr(self.setting, "og_image", None):
            image = self.setting.og_image
        elif self.default is not None and getattr(self.default, "default_og_image", None):
            image = self.default.default_og_image

        self._cache["og_image"] = image
        return image

    @property
    def og_image_url(self):
        image = self.og_image
        if image:
            try:
                return image.url
            except Exception:
                return ""
        # ✅ اصلاح: request را پاس می‌دهیم
        return _build_absolute(self.request, _default_og_image_url())

    # =====================
    #  Twitter Card
    # =====================

    @property
    def twitter_card(self):
        return self._pick(
            getattr(self.setting, "twitter_card", None) if self.setting else None,
        ) or "summary_large_image"

    @property
    def twitter_title(self):
        return self._pick(
            getattr(self.setting, "twitter_title", None) if self.setting else None,
            self.og_title,
        ) or ""

    @property
    def twitter_description(self):
        return self._pick(
            getattr(self.setting, "twitter_description", None) if self.setting else None,
            self.og_description,
        ) or ""

    @property
    def twitter_image(self):
        if self.setting is not None and getattr(self.setting, "twitter_image", None):
            return self.setting.twitter_image
        return self.og_image

    @property
    def twitter_image_url(self):
        image = self.twitter_image
        if image:
            try:
                return image.url
            except Exception:
                return ""
        return self.og_image_url

    # =====================
    #  Yoast
    # =====================

    @property
    def focus_keyphrase(self):
        return self._pick(
            getattr(self.setting, "focus_keyphrase", None) if self.setting else None,
        ) or ""

    @property
    def seo_score(self):
        if self.setting is not None:
            return getattr(self.setting, "seo_score", 0) or 0
        return 0

    @property
    def schema_type(self):
        manual = getattr(self.setting, "schema_type", None) if self.setting else None
        if manual and manual != "auto":
            return manual

        mapping = {
            "page": "WebPage",
            "product": "Product",
            "blog": "Article",
            "news": "NewsArticle",
            "media": "VideoObject",
            "resume": "Person",
        }
        return mapping.get(self.content_type, "WebPage")

    @property
    def schema_json(self):
        if self.setting is not None and getattr(self.setting, "schema_json", None):
            return self.setting.schema_json
        return None

    @property
    def breadcrumb_title(self):
        return self._pick(
            getattr(self.setting, "breadcrumb_title", None) if self.setting else None,
            self.title,
        ) or ""

    @property
    def hreflang_group(self):
        return self._pick(
            getattr(self.setting, "hreflang_group", None) if self.setting else None,
        ) or ""

    # =====================
    #  زمان‌بندی
    # =====================

    @property
    def publish_status(self):
        return self._pick(
            getattr(self.setting, "publish_status", None) if self.setting else None,
        ) or "published"

    @property
    def is_published_now(self):
        if self.setting is None:
            return True
        try:
            return self.setting.is_published_now()
        except Exception:
            return True

    # =====================
    #  Hreflang
    # =====================

    @property
    def hreflang(self):
        if "hreflang" in self._cache:
            return self._cache["hreflang"]

        group = self.hreflang_group

        if not group:
            self._cache["hreflang"] = []
            return []

        siblings = (
            SEOSetting.objects
            .filter(
                is_active=True,
                hreflang_group=group,
            )
            .exclude(pk=getattr(self.setting, "pk", None))
        )

        current_lang = _detect_language(self.request)

        result = [
            {
                "lang": current_lang,
                "url": self.canonical or "",
                "is_current": True,
            }
        ]

        for sib in siblings:
            lang = "fa"
            if sib.url and "/en/" in sib.url:
                lang = "en"
            elif sib.url and sib.url.startswith("en."):
                lang = "en"

            result.append({
                "lang": lang,
                "url": sib.canonical or sib.url or "",
                "is_current": False,
            })

        self._cache["hreflang"] = result
        return result

    # =====================
    #  Breadcrumb
    # =====================

    @property
    def breadcrumb(self):
        if "breadcrumb" in self._cache:
            return self._cache["breadcrumb"]

        items = []

        home_url = _site_base_url() or "/"
        home_label = "خانه" if _detect_language(self.request) == "fa" else "Home"

        items.append({
            "label": home_label,
            "url": home_url,
            "position": 1,
        })

        if self.content_type != "page" and self.obj is not None:
            parent = getattr(self.obj, "category", None)
            if parent:
                items.append({
                    "label": str(parent),
                    "url": getattr(parent, "get_absolute_url", lambda: "")() or "",
                    "position": len(items) + 1,
                })

        items.append({
            "label": self.breadcrumb_title,
            "url": self.canonical or "",
            "position": len(items) + 1,
        })

        self._cache["breadcrumb"] = items
        return items

    # =====================
    #  Schema  —  وصل به schema.py
    # =====================

    @property
    def schema(self):
        if "schema" in self._cache:
            return self._cache["schema"]

        from .schema import generate_schema

        result = generate_schema(self, obj=self.obj)
        self._cache["schema"] = result
        return result

    @property
    def schema_json_ld(self):
        """JSON string معتبر برای قرار گرفتن داخل <script>."""
        if "schema_json_ld" in self._cache:
            return self._cache["schema_json_ld"]

        schema = self.schema
        if not schema:
            self._cache["schema_json_ld"] = ""
            return ""

        try:
            result = json.dumps(schema, ensure_ascii=False)
        except (TypeError, ValueError):
            result = ""

        self._cache["schema_json_ld"] = result
        return result

    # =====================
    #  Debug
    # =====================

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<SEOContext page_key={self.page_key} type={self.content_type}>"


# =====================================================
#  SEOManager
# =====================================================

class SEOManager:

    @staticmethod
    def get_page(page_key):
        if not page_key:
            return SEOContext()

        request = get_current_request()
        language = _detect_language(request)

        setting = (
            SEOSetting.objects
            .filter(
                content_type="page",
                page_key=page_key,
                is_active=True,
            )
            .first()
        )

        default = (
            SEODefault.objects
            .filter(
                language=language,
                content_type="page",
                is_active=True,
            )
            .first()
        )

        return SEOContext(
            setting=setting,
            default=default,
            page_key=page_key,
            content_type="page",
            request=request,
        )

    @staticmethod
    def get_object(instance):
        if not instance:
            return SEOContext()

        request = get_current_request()

        content_type = ContentType.objects.get_for_model(instance.__class__)

        setting = (
            SEOSetting.objects
            .filter(
                app_label=content_type.app_label,
                model_name=content_type.model,
                object_id=instance.pk,
                is_active=True,
            )
            .first()
        )

        ct_map = {
            "product": "product",
            "blog": "blog",
            "news": "news",
            "media": "media",
            "resume": "resume",
        }

        internal_ct = ct_map.get(content_type.model, "other")

        language = _detect_language(request)

        default = (
            SEODefault.objects
            .filter(
                language=language,
                content_type=internal_ct,
                is_active=True,
            )
            .first()
        )

        return SEOContext(
            setting=setting,
            default=default,
            obj=instance,
            content_type=internal_ct,
            request=request,
        )

    @staticmethod
    def get_by_id(app_label, model_name, object_id):
        if not app_label or not model_name or not object_id:
            return SEOContext()

        request = get_current_request()

        setting = (
            SEOSetting.objects
            .filter(
                app_label=app_label,
                model_name=model_name,
                object_id=object_id,
                is_active=True,
            )
            .first()
        )

        return SEOContext(
            setting=setting,
            content_type="other",
            request=request,
        )