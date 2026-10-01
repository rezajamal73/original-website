# app_seo/signals.py

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps

from .models import SEOSetting


# =====================================================
#  نگاشت مدل‌ها به content_type داخلی
# =====================================================

MODEL_TO_CONTENT_TYPE = {
    "product": "product",
    "blog": "blog",
    "news": "news",
    "media": "media",
    "resume": "resume",
}


# =====================================================
#  همگام‌سازی Robots  —  pre_save
# =====================================================

@receiver(pre_save, sender=SEOSetting, dispatch_uid="seo_sync_robots")
def sync_robots(sender, instance, **kwargs):
    """
    همگام‌سازی دو طرفه بین فیلد قدیمی robots و
    فیلدهای جدید index_control / follow_control.
    """

    if not instance.pk:
        # رکورد جدید — از index/follow بساز
        if instance.index_control and instance.follow_control:
            instance.robots = (
                f"{instance.index_control},{instance.follow_control}"
            )
        return

    # رکورد موجود — ببین کدام سمت عوض شده
    try:
        old = SEOSetting.objects.get(pk=instance.pk)
    except SEOSetting.DoesNotExist:
        return

    robots_changed = old.robots != instance.robots
    index_changed = old.index_control != instance.index_control
    follow_changed = old.follow_control != instance.follow_control

    if index_changed or follow_changed:
        # index/follow دست خورده → robots را بساز
        instance.robots = (
            f"{instance.index_control},{instance.follow_control}"
        )

    elif robots_changed:
        # robots دست خورده → index/follow را بساز
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
    """
    اگر عنوان یا focus_keyphrase عوض شد، امتیاز را تحلیل کن.
    برای جلوگیری از حلقه، از update_fields استفاده می‌کنیم.
    """

    update_fields = kwargs.get("update_fields") or set()

    # اگر خود analyzer ذخیره کرده، دوباره تحلیل نکن
    if "seo_score" in update_fields:
        return

    # فقط اگر عنوان یا keyphrase تغییر کرده
    trigger_fields = {"title", "description", "focus_keyphrase",
                      "canonical", "robots", "index_control",
                      "follow_control", "og_title", "og_description"}

    if update_fields and not (update_fields & trigger_fields):
        return

    try:
        from .analyzer import analyze_and_save
        analyze_and_save(instance)
    except Exception:
        # تحلیل نباید باعث خطا در ذخیره شود
        pass


# =====================================================
#  ساخت خودکار SEOSetting برای محتوای جدید
# =====================================================

def _ensure_seo_setting(instance):
    """
    اگر SEOSetting برای این آبجکت وجود ندارد، یک رکورد خالی بساز.
    """

    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(instance.__class__)
    except Exception:
        return

    content_type = MODEL_TO_CONTENT_TYPE.get(ct.model)

    if not content_type:
        return

    # بررسی وجود
    exists = SEOSetting.objects.filter(
        app_label=ct.app_label,
        model_name=ct.model,
        object_id=instance.pk,
    ).exists()

    if exists:
        return

    # عنوان پیش‌فرض از آبجکت
    title = (
        getattr(instance, "title_fa", None)
        or getattr(instance, "title_en", None)
        or getattr(instance, "title", None)
        or ""
    )

    description = (
        getattr(instance, "description_fa", None)
        or getattr(instance, "description_en", None)
        or getattr(instance, "description", None)
        or ""
    )

    SEOSetting.objects.create(
        content_type=content_type,
        app_label=ct.app_label,
        model_name=ct.model,
        object_id=instance.pk,
        title=title[:70] if title else "بدون عنوان",
        description=description[:160] if description else "",
        is_active=True,
    )


@receiver(post_save, sender=apps.get_model("app_product", "Product"),
          dispatch_uid="seo_product_post_save")
def product_post_save(sender, instance, created, **kwargs):
    _ensure_seo_setting(instance)


@receiver(post_save, sender=apps.get_model("app_blog", "blog"),
          dispatch_uid="seo_blog_post_save")
def blog_post_save(sender, instance, created, **kwargs):
    _ensure_seo_setting(instance)


@receiver(post_save, sender=apps.get_model("app_news", "News"),
          dispatch_uid="seo_news_post_save")
def news_post_save(sender, instance, created, **kwargs):
    _ensure_seo_setting(instance)


# =====================================================
#  حذف SEOSetting وقتی آبجکت حذف می‌شود
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


@receiver(post_delete, sender=apps.get_model("app_product", "Product"),
          dispatch_uid="seo_product_post_delete")
def product_post_delete(sender, instance, **kwargs):
    _delete_seo_setting(instance)


@receiver(post_delete, sender=apps.get_model("app_blog", "blog"),
          dispatch_uid="seo_blog_post_delete")
def blog_post_delete(sender, instance, **kwargs):
    _delete_seo_setting(instance)


@receiver(post_delete, sender=apps.get_model("app_news", "News"),
          dispatch_uid="seo_news_post_delete")
def news_post_delete(sender, instance, **kwargs):
    _delete_seo_setting(instance)