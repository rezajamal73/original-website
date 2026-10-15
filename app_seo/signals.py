# app_seo/signals.py

"""
سیگنال‌های app_seo.

- هیچ مدل خارجی در سطح ماژول import نمی‌شود.
- اتصال از AppConfig.ready() با connect_lazy_receivers() انجام می‌شود.
- همه‌ی اپ‌های پروژه پوشش داده شده‌اند.
"""

from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import SEOSetting


# =====================================================
#  نگاشت مرکزی  —  (app_label, model_name) → content_type
# =====================================================

MODEL_TO_CONTENT_TYPE = {

    ("app_product", "product"): "product",
    ("app_blog", "blog"): "blog",
    ("app_news", "news"): "news",
    ("app_media", "media"): "media",
    ("app_resume", "resume"): "resume",
    ("app_tender", "tender"): "tender",
    ("app_tender_holding", "holding"): "holding",
    ("app_auction", "auction"): "auction",
    ("app_catalog", "companycatalog"): "catalog",
    ("app_hr", "jobopportunity"): "hr",
    ("app_chart", "person"): "chart",
    ("app_chart", "boardmember"): "chart",
    ("app_inquiry", "purchaseinquiry"): "other",
}


# =====================================================
#  همگام‌سازی Robots  —  pre_save
# =====================================================

@receiver(pre_save, sender=SEOSetting, dispatch_uid="seo_sync_robots")
def sync_robots(sender, instance, **kwargs):
    if not instance.pk:
        if instance.index_control and instance.follow_control:
            instance.robots = (
                f"{instance.index_control},{instance.follow_control}"
            )
        return

    try:
        old = SEOSetting.objects.get(pk=instance.pk)
    except SEOSetting.DoesNotExist:
        return

    robots_changed = old.robots != instance.robots
    index_changed = old.index_control != instance.index_control
    follow_changed = old.follow_control != instance.follow_control

    if index_changed or follow_changed:
        instance.robots = (
            f"{instance.index_control},{instance.follow_control}"
        )
    elif robots_changed:
        parts = (instance.robots or "").split(",")
        index = parts[0].strip() if parts else "index"
        follow = parts[1].strip() if len(parts) > 1 else "follow"

        if index in ("index", "noindex"):
            instance.index_control = index
        if follow in ("follow", "nofollow"):
            instance.follow_control = follow


# =====================================================
#  تحلیل خودکار پس از ذخیره SEOSetting
# =====================================================

@receiver(post_save, sender=SEOSetting, dispatch_uid="seo_auto_analyze")
def auto_analyze(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields") or set()

    if "seo_score" in update_fields:
        return

    trigger_fields = {
        "title", "title_en",
        "description", "description_en",
        "focus_keyphrase",
        "canonical", "robots", "index_control",
        "follow_control", "og_title", "og_title_en",
        "og_description", "og_description_en",
        "twitter_title", "twitter_title_en",
        "twitter_description", "twitter_description_en",
        "schema_type", "schema_json",
        "breadcrumb_title", "breadcrumb_title_en",
        "keywords",
    }

    if update_fields and not (update_fields & trigger_fields):
        return

    try:
        from .analyzer import analyze_and_save
        analyze_and_save(instance)
    except Exception:
        pass


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get(obj, *names, default=None):
    """خواندن امن اولین فیلد غیرخالی."""
    for name in names:
        value = getattr(obj, name, None)
        if value is not None and value != "":
            return value
    return default


def _extract_title_smart(instance, lang="fa"):
    """
    ✅ استخراج هوشمند عنوان از هر مدل.

    اولویت:
    1. فیلدهای دقیق و شناخته‌شده
    2. فیلدهای شامل کلمات کلیدی (project, hospital, company, ...)
    3. اولین فیلد متنی غیرخالی
    """

    # ---- الگوهای دقیق ----
    if lang == "fa":
        exact = [
            "title_fa", "title",
            "name_fa", "name",
            "full_name_fa", "full_name",
            "project_name_fa", "project_name",
            "hospital_name_fa", "hospital_name",
            "company_name_fa", "company_name",
            "clinic_name_fa", "clinic_name",
            "center_name_fa", "center_name",
        ]
        patterns = [
            "project", "hospital", "company", "clinic",
            "center", "organization", "name", "title",
        ]
    else:
        exact = [
            "title_en", "name_en", "full_name_en",
            "project_name_en",
            "hospital_name_en",
            "company_name_en",
            "clinic_name_en",
            "center_name_en",
        ]
        patterns = [
            "project", "hospital", "company", "clinic",
            "center", "organization", "name", "title",
        ]

    # ---- 1. فیلدهای دقیق ----
    for f in exact:
        val = getattr(instance, f, None)
        if val and isinstance(val, str) and val.strip():
            return val

    # ---- 2. فیلدهای شامل الگو ----
    try:
        fields = instance._meta.get_fields()
    except Exception:
        return ""

    for field in fields:
        name = field.name

        if not hasattr(instance, name):
            continue

        if field.get_internal_type() not in (
            "CharField", "TextField", "SlugField"
        ):
            continue

        # چک زبان
        if lang == "fa" and name.endswith("_en"):
            continue
        if lang == "en" and name.endswith("_fa"):
            continue

        for pattern in patterns:
            if pattern in name.lower():
                val = getattr(instance, name, None)
                if val and isinstance(val, str) and val.strip():
                    return val

    return ""


def _extract_description_smart(instance, lang="fa"):
    """
    ✅ استخراج هوشمند توضیحات از هر مدل.
    """
    if lang == "fa":
        exact = [
            "description_fa", "description",
            "summary_fa", "summary",
            "short_description_fa", "short_description",
            "meta_description_fa", "meta_description",
            "address_fa", "address",
            "content_fa", "content",
        ]
    else:
        exact = [
            "description_en", "summary_en",
            "short_description_en", "meta_description_en",
            "address_en", "content_en",
        ]

    for f in exact:
        val = getattr(instance, f, None)
        if val and isinstance(val, str) and val.strip():
            return val

    return ""


def _extract_image(instance, *fields):
    """
    استخراج اولین تصویر موجود از مدل.
    """
    for field in fields:
        img = getattr(instance, field, None)
        if img:
            try:
                if hasattr(img, "url") and img.url:
                    return img
            except Exception:
                continue
    return None


def _build_hreflang_group(instance, ct):
    """
    ساخت خودکار hreflang_group.
    فرمت: {app_label}.{model_name}.{object_id}
    """
    return f"{ct.app_label}.{ct.model}.{instance.pk}"


def _extract_keywords(instance, title_fa, title_en):
    """
    استخراج هوشمند کلمات کلیدی.
    """

    # 1. فیلد keywords
    keywords = _get(instance, "keywords", default="")

    # 2. فیلد tags (ManyToMany)
    if not keywords:
        tags = getattr(instance, "tags", None)
        if tags is not None:
            try:
                keywords = ", ".join(str(t) for t in tags.all())
            except Exception:
                keywords = ""

    if keywords and not isinstance(keywords, str):
        try:
            keywords = ", ".join(str(t) for t in keywords.all())
        except Exception:
            keywords = ""

    if keywords:
        return keywords

    # 3. ساخت از عنوان + دسته‌بندی + برند
    parts = []

    if title_fa:
        parts.append(str(title_fa).strip())
    if title_en:
        parts.append(str(title_en).strip())

    # دسته‌بندی
    category = (
        getattr(instance, "category", None)
        or getattr(instance, "category2", None)
    )
    if category:
        cat_title = (
            getattr(category, "title_fa", None)
            or getattr(category, "title", None)
            or getattr(category, "title_en", None)
        )
        if cat_title:
            parts.append(str(cat_title).strip())

    # استان/شهر (برای resume)
    province = (
        getattr(instance, "province", None)
        or getattr(instance, "city", None)
        or getattr(instance, "state", None)
    )
    if province:
        prov_name = (
            getattr(province, "name_fa", None)
            or getattr(province, "name", None)
            or getattr(province, "title", None)
            or str(province)
        )
        if prov_name:
            parts.append(str(prov_name).strip())

    # حذف تکراری‌ها
    seen = set()
    unique = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            unique.append(p)

    return ", ".join(unique)


def _extract_all_fields(instance):
    """
    استخراج تمام فیلدهای قابل استفاده برای SEOSetting از یک مدل.
    """

    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(instance.__class__)
    except Exception:
        ct = None

    # =====================
    #  عنوان‌ها  —  ✅ هوشمند
    # =====================

    title_fa = _extract_title_smart(instance, lang="fa")
    title_en = _extract_title_smart(instance, lang="en")

    # =====================
    #  توضیحات  —  ✅ هوشمند
    # =====================

    description_fa = _extract_description_smart(instance, lang="fa")
    description_en = _extract_description_smart(instance, lang="en")

    # =====================
    #  کلمات کلیدی
    # =====================

    keywords = _extract_keywords(instance, title_fa, title_en)

    # =====================
    #  Canonical
    # =====================

    canonical = ""

    try:
        get_url = getattr(instance, "get_absolute_url", None)
        if callable(get_url):
            canonical = get_url() or ""
    except Exception:
        canonical = ""

    if not canonical:
        canonical = _get(instance, "url", "canonical", default="")

    # =====================
    #  Focus Keyphrase
    # =====================

    focus_keyphrase = _get(
        instance,
        "focus_keyphrase",
        "meta_keyphrase",
        "primary_keyword",
        default="",
    )

    if not focus_keyphrase and title_fa:
        focus_keyphrase = " ".join(str(title_fa).split()[:3])

    # =====================
    #  تصویر اصلی
    # =====================

    main_image = _extract_image(
        instance,
        "main_image", "image", "cover",
        "thumbnail", "picture", "photo",
        "image_fa", "image_en", "svg",
    )

    # =====================
    #  Open Graph
    # =====================

    og_title = _get(instance, "og_title", default="")
    og_title_en = _get(instance, "og_title_en", default="")
    og_description = _get(instance, "og_description", default="")
    og_description_en = _get(instance, "og_description_en", default="")

    # =====================
    #  Twitter Card
    # =====================

    twitter_title = _get(instance, "twitter_title", default="")
    twitter_title_en = _get(instance, "twitter_title_en", default="")
    twitter_description = _get(instance, "twitter_description", default="")
    twitter_description_en = _get(instance, "twitter_description_en", default="")

    # =====================
    #  Schema
    # =====================

    schema_type = _get(instance, "schema_type", default="auto")
    schema_json = _get(instance, "schema_json", default=None)

    # =====================
    #  Breadcrumb
    # =====================

    breadcrumb_title = _get(instance, "breadcrumb_title", default="")
    breadcrumb_title_en = _get(instance, "breadcrumb_title_en", default="")

    # =====================
    #  Hreflang خودکار
    # =====================

    hreflang_group = _get(instance, "hreflang_group", default="")

    if not hreflang_group and ct is not None and instance.pk:
        hreflang_group = _build_hreflang_group(instance, ct)

    # =====================
    #  زمان‌بندی
    # =====================

    publish_status = _get(instance, "publish_status", default="published")
    publish_at = _get(instance, "publish_at", "publish_date", default=None)
    expire_at = _get(instance, "expire_at", "expire_date", default=None)

    # =====================
    #  Robots
    # =====================

    index_control = _get(instance, "index_control", default="index")
    follow_control = _get(instance, "follow_control", default="follow")

    # =====================
    #  بازگشت
    # =====================

    return {
        # عنوان
        "title": (title_fa or "")[:70],
        "title_en": (title_en or "")[:70],

        # توضیحات
        "description": (description_fa or "")[:160],
        "description_en": (description_en or "")[:160],

        # کلمات کلیدی
        "keywords": keywords or "",

        # Canonical
        "canonical": canonical or "",

        # Focus Keyphrase
        "focus_keyphrase": (focus_keyphrase or "")[:120],

        # تصاویر
        "og_image": main_image,
        "twitter_image": main_image,

        # Open Graph
        "og_title": (og_title or title_fa or "")[:70],
        "og_title_en": (og_title_en or title_en or "")[:70],
        "og_description": (og_description or description_fa or "")[:160],
        "og_description_en": (og_description_en or description_en or "")[:160],

        # Twitter
        "twitter_title": (twitter_title or og_title or title_fa or "")[:70],
        "twitter_title_en": (twitter_title_en or og_title_en or title_en or "")[:70],
        "twitter_description": (twitter_description or og_description or description_fa or "")[:160],
        "twitter_description_en": (twitter_description_en or og_description_en or description_en or "")[:160],

        # Schema
        "schema_type": schema_type or "auto",
        "schema_json": schema_json,

        # Breadcrumb
        "breadcrumb_title": (breadcrumb_title or title_fa or "")[:120],
        "breadcrumb_title_en": (breadcrumb_title_en or title_en or "")[:120],

        # Hreflang خودکار
        "hreflang_group": hreflang_group or "",

        # زمان‌بندی
        "publish_status": publish_status or "published",
        "publish_at": publish_at,
        "expire_at": expire_at,

        # Robots
        "index_control": index_control or "index",
        "follow_control": follow_control or "follow",
    }


# =====================================================
#  ساخت خودکار SEOSetting برای محتوای جدید
# =====================================================

def _ensure_seo_setting(instance):
    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(instance.__class__)
    except Exception:
        return

    content_type = MODEL_TO_CONTENT_TYPE.get((ct.app_label, ct.model))

    if not content_type:
        return

    exists = SEOSetting.objects.filter(
        app_label=ct.app_label,
        model_name=ct.model,
        object_id=instance.pk,
    ).exists()

    if exists:
        return

    data = _extract_all_fields(instance)

    if not data["title"]:
        data["title"] = "بدون عنوان"

    if not data.get("og_image"):
        data.pop("og_image", None)
    if not data.get("twitter_image"):
        data.pop("twitter_image", None)

    try:
        SEOSetting.objects.create(
            content_type=content_type,
            app_label=ct.app_label,
            model_name=ct.model,
            object_id=instance.pk,
            is_active=True,
            **data,
        )
    except Exception:
        pass


# =====================================================
#  به‌روزرسانی خودکار SEOSetting موجود
# =====================================================

def _update_seo_setting(instance, force=False):
    """
    فقط فیلدهای خالی SEOSetting را از مدل پر می‌کند.
    اگر force=True باشد، همه فیلدها را بازنویسی می‌کند.
    """
    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(instance.__class__)
    except Exception:
        return

    content_type = MODEL_TO_CONTENT_TYPE.get((ct.app_label, ct.model))

    if not content_type:
        return

    seo = SEOSetting.objects.filter(
        app_label=ct.app_label,
        model_name=ct.model,
        object_id=instance.pk,
    ).first()

    if not seo:
        return

    data = _extract_all_fields(instance)

    fields_to_update = []

    for field, value in data.items():

        # فیلدهای خاص
        if field in ("publish_status", "index_control", "follow_control"):
            continue

        # فیلدهای تصویری
        if field in ("og_image", "twitter_image"):
            current = getattr(seo, field, None)
            if not current and value:
                setattr(seo, field, value)
                fields_to_update.append(field)
            continue

        # فیلدهای معمولی
        current = getattr(seo, field, None)

        if force:
            # بازنویسی همه
            if value not in (None, "", []):
                setattr(seo, field, value)
                fields_to_update.append(field)
        else:
            # فقط خالی‌ها
            if current in (None, "", []):
                if value not in (None, "", []):
                    setattr(seo, field, value)
                    fields_to_update.append(field)

    if fields_to_update:
        try:
            seo.save(update_fields=fields_to_update)
        except Exception:
            pass


# =====================================================
#  حذف SEOSetting
# =====================================================

def _delete_seo_setting(instance):
    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(instance.__class__)
    except Exception:
        return

    SEOSetting.objects.filter(
        app_label=ct.app_label,
        model_name=ct.model,
        object_id=instance.pk,
    ).delete()


# =====================================================
#  هندلرهای عمومی
# =====================================================

def _generic_post_save(sender, instance, created, **kwargs):
    if created:
        _ensure_seo_setting(instance)
    else:
        _update_seo_setting(instance)


def _generic_post_delete(sender, instance, **kwargs):
    _delete_seo_setting(instance)


# =====================================================
#  اتصال lazy رسیورها
# =====================================================

def connect_lazy_receivers():
    connected = 0

    for (app_label, model_name), _ in MODEL_TO_CONTENT_TYPE.items():

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        if model is None:
            continue

        post_save.connect(
            _generic_post_save,
            sender=model,
            dispatch_uid=f"seo_{app_label}_{model_name}_post_save",
        )

        post_delete.connect(
            _generic_post_delete,
            sender=model,
            dispatch_uid=f"seo_{app_label}_{model_name}_post_delete",
        )

        connected += 1

    return connected


def disconnect_lazy_receivers():
    for (app_label, model_name), _ in MODEL_TO_CONTENT_TYPE.items():

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        if model is None:
            continue

        post_save.disconnect(
            sender=model,
            dispatch_uid=f"seo_{app_label}_{model_name}_post_save",
        )
        post_delete.disconnect(
            sender=model,
            dispatch_uid=f"seo_{app_label}_{model_name}_post_delete",
        )