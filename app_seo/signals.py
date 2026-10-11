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
#
#  این نگاشت بر اساس appهایی که تو پروژه داری ساخته شده:
#   app_product, app_blog, app_news, app_media, app_resume,
#   app_tender, app_tender_holding, app_auction, app_catalog,
#   app_hr, app_chart, app_inquiry
#
#  اگه اسم مدل با اسمی که اینجا نوشته فرق داره، اصلاحش کن.
#

MODEL_TO_CONTENT_TYPE = {

    # ---- محتوای اصلی ----
    ("app_product", "product"): "product",
    ("app_blog", "blog"): "blog",
    ("app_news", "news"): "news",
    ("app_media", "media"): "media",
    ("app_resume", "resume"): "resume",

    # ---- مناقصات / مزایدات ----
    ("app_tender", "tender"): "tender",
    ("app_tender_holding", "holding"): "holding",
    ("app_auction", "auction"): "auction",

    # ---- کاتالوگ ----
    ("app_catalog", "companycatalog"): "catalog",        # ✅ اصلاح

    # ---- منابع انسانی ----
    ("app_hr", "jobopportunity"): "hr",                  # ✅ اصلاح

    # ---- چارت سازمانی ----
    ("app_chart", "person"): "chart",
    ("app_chart", "boardmember"): "chart",               # ✅ اضافه شد

    # ---- استعلام خرید ----
    ("app_inquiry", "purchaseinquiry"): "other",         # ✅ اصلاح
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
#  پس از ذخیره SEOSetting  —  تحلیل خودکار
# =====================================================

@receiver(post_save, sender=SEOSetting, dispatch_uid="seo_auto_analyze")
def auto_analyze(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields") or set()

    if "seo_score" in update_fields:
        return

    trigger_fields = {
        "title", "description", "focus_keyphrase",
        "canonical", "robots", "index_control",
        "follow_control", "og_title", "og_description",
    }

    if update_fields and not (update_fields & trigger_fields):
        return

    try:
        from .analyzer import analyze_and_save
        analyze_and_save(instance)
    except Exception:
        pass


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

    title = (
        getattr(instance, "title_fa", None)
        or getattr(instance, "title_en", None)
        or getattr(instance, "title", None)
        or getattr(instance, "name", None)
        or getattr(instance, "full_name", None)
        or ""
    )

    description = (
        getattr(instance, "description_fa", None)
        or getattr(instance, "description_en", None)
        or getattr(instance, "description", None)
        or getattr(instance, "summary_fa", None)
        or getattr(instance, "summary_en", None)
        or ""
    )

    try:
        SEOSetting.objects.create(
            content_type=content_type,
            app_label=ct.app_label,
            model_name=ct.model,
            object_id=instance.pk,
            title=title[:70] if title else "بدون عنوان",
            description=description[:160] if description else "",
            is_active=True,
        )
    except Exception:
        pass


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
    _ensure_seo_setting(instance)


def _generic_post_delete(sender, instance, **kwargs):
    _delete_seo_setting(instance)


# =====================================================
#  اتصال lazy رسیورها  —  از AppConfig.ready() صدا زده می‌شود
# =====================================================

def connect_lazy_receivers():
    """
    برای هر (app_label, model_name) در MODEL_TO_CONTENT_TYPE،
    مدل را از registry می‌گیرد و اگر وجود داشت، رسیورها را وصل می‌کند.
    """
    connected = 0

    for (app_label, model_name), _ in MODEL_TO_CONTENT_TYPE.items():

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            # این app یا مدل نصب نیست — بی‌صدا رد شو
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