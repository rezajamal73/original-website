
# app_seo/signals.py

"""
Automatic SEO synchronization.

- Connect model receivers from AppConfig.ready().
- Create SEO settings for newly created content.
- Fill only empty SEO fields on ordinary updates.
- Preserve manually entered SEO data.
- Delete related SEO records when content is deleted.
- Log synchronization failures.
"""

import logging

from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import SEOSetting


logger = logging.getLogger(__name__)


# ============================================================
# Model mapping
# ============================================================

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


# ============================================================
# General helpers
# ============================================================

def _get(obj, *names, default=None):
    if obj is None:
        return default

    for name in names:
        try:
            value = getattr(obj, name, None)
        except (AttributeError, ValueError):
            continue

        if value is not None and value != "":
            return value

    return default


def _text(value, limit=None):
    if value is None:
        return ""

    value = str(value).strip()

    if limit is not None:
        value = value[:limit]

    return value


def _model_fields(instance):
    return {
        field.name: field
        for field in instance._meta.concrete_fields
    }


def _safe_model_value(instance, name):
    fields = _model_fields(instance)

    if name not in fields:
        return None

    try:
        return getattr(instance, name, None)
    except (AttributeError, ValueError):
        return None


def _first_text_field(instance, names):
    fields = _model_fields(instance)

    for name in names:
        field = fields.get(name)

        if field is None:
            continue

        if field.get_internal_type() not in (
            "CharField",
            "TextField",
            "SlugField",
        ):
            continue

        value = _safe_model_value(instance, name)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


# ============================================================
# Robots synchronization
# ============================================================

@receiver(
    pre_save,
    sender=SEOSetting,
    dispatch_uid="seo_sync_robots",
)
def sync_robots(sender, instance, **kwargs):
    index = instance.index_control or "index"
    follow = instance.follow_control or "follow"

    if not instance.pk:
        instance.robots = f"{index},{follow}"
        return

    try:
        old = SEOSetting.objects.get(pk=instance.pk)
    except SEOSetting.DoesNotExist:
        instance.robots = f"{index},{follow}"
        return

    index_changed = (
        old.index_control != instance.index_control
    )

    follow_changed = (
        old.follow_control != instance.follow_control
    )

    robots_changed = (
        old.robots != instance.robots
    )

    if index_changed or follow_changed:
        instance.robots = f"{index},{follow}"

    elif robots_changed:
        parts = [
            part.strip().lower()
            for part in (instance.robots or "").split(",")
        ]

        new_index = parts[0] if parts else "index"

        new_follow = (
            parts[1]
            if len(parts) > 1
            else "follow"
        )

        if new_index in ("index", "noindex"):
            instance.index_control = new_index

        if new_follow in ("follow", "nofollow"):
            instance.follow_control = new_follow


# ============================================================
# Automatic SEO analysis
# ============================================================

@receiver(
    post_save,
    sender=SEOSetting,
    dispatch_uid="seo_auto_analyze",
)
def auto_analyze(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields")

    if update_fields is not None:
        update_fields = set(update_fields)

        if "seo_score" in update_fields:
            return

    trigger_fields = {
        "title",
        "title_en",
        "description",
        "description_en",
        "focus_keyphrase",
        "canonical",
        "robots",
        "index_control",
        "follow_control",
        "og_title",
        "og_title_en",
        "og_description",
        "og_description_en",
        "twitter_title",
        "twitter_title_en",
        "twitter_description",
        "twitter_description_en",
        "schema_type",
        "schema_json",
        "breadcrumb_title",
        "breadcrumb_title_en",
        "keywords",
    }

    if (
        update_fields is not None
        and not (update_fields & trigger_fields)
    ):
        return

    try:
        from .analyzer import analyze_and_save

        analyze_and_save(instance)

    except Exception:
        logger.exception(
            "SEO automatic analysis failed for SEOSetting %s",
            instance.pk,
        )


# ============================================================
# Smart title extraction
# ============================================================

def _extract_title_smart(instance, lang="fa"):
    if lang == "en":
        names = [
            "title_en",
            "name_en",
            "full_name_en",
            "project_name_en",
            "hospital_name_en",
            "company_name_en",
            "clinic_name_en",
            "center_name_en",
        ]
    else:
        names = [
            "title_fa",
            "title",
            "name_fa",
            "name",
            "full_name_fa",
            "full_name",
            "project_name_fa",
            "project_name",
            "hospital_name_fa",
            "hospital_name",
            "company_name_fa",
            "company_name",
            "clinic_name_fa",
            "clinic_name",
            "center_name_fa",
            "center_name",
        ]

    title = _first_text_field(instance, names)

    if title:
        return title

    patterns = (
        "project",
        "hospital",
        "company",
        "clinic",
        "center",
        "organization",
        "name",
        "title",
    )

    fields = _model_fields(instance)

    for name, field in fields.items():
        if field.get_internal_type() not in (
            "CharField",
            "TextField",
            "SlugField",
        ):
            continue

        if lang == "fa" and name.endswith("_en"):
            continue

        if lang == "en" and name.endswith("_fa"):
            continue

        if not any(pattern in name.lower() for pattern in patterns):
            continue

        value = _safe_model_value(instance, name)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


# ============================================================
# Smart description extraction
# ============================================================

def _extract_description_smart(instance, lang="fa"):
    if lang == "en":
        names = [
            "description_en",
            "summary_en",
            "short_description_en",
            "meta_description_en",
            "address_en",
            "content_en",
        ]
    else:
        names = [
            "description_fa",
            "description",
            "summary_fa",
            "summary",
            "short_description_fa",
            "short_description",
            "meta_description_fa",
            "meta_description",
            "address_fa",
            "address",
            "content_fa",
            "content",
        ]

    return _first_text_field(instance, names)


# ============================================================
# Image extraction
# ============================================================

def _extract_image(instance, *fields):
    model_fields = _model_fields(instance)

    for name in fields:
        if name not in model_fields:
            continue

        image = _safe_model_value(instance, name)

        if not image:
            continue

        try:
            if image.url:
                return image
        except (AttributeError, ValueError, OSError):
            continue

    return None


# ============================================================
# Hreflang grouping
# ============================================================

def _build_hreflang_group(instance, ct):
    return (
        f"{ct.app_label}."
        f"{ct.model}."
        f"{instance.pk}"
    )


# ============================================================
# Keywords
# ============================================================

def _extract_keywords(instance, title_fa, title_en):
    keywords = _get(
        instance,
        "keywords",
        default="",
    )

    if isinstance(keywords, str) and keywords.strip():
        return keywords.strip()

    if keywords:
        try:
            return ", ".join(
                str(item)
                for item in keywords.all()
            )
        except (AttributeError, TypeError, ValueError):
            pass

    tags = _get(instance, "tags")

    if tags is not None:
        try:
            result = ", ".join(
                str(item)
                for item in tags.all()
            )

            if result:
                return result

        except (AttributeError, TypeError, ValueError):
            pass

    parts = []

    if title_fa:
        parts.append(title_fa)

    if title_en:
        parts.append(title_en)

    category = _get(
        instance,
        "category",
        "category2",
    )

    if category:
        category_title = _get(
            category,
            "title_fa",
            "title",
            "title_en",
        )

        if category_title:
            parts.append(str(category_title))

    location = _get(
        instance,
        "province",
        "city",
        "state",
    )

    if location:
        location_name = _get(
            location,
            "name_fa",
            "name",
            "title",
        )

        if location_name:
            parts.append(str(location_name))

    seen = set()
    unique = []

    for part in parts:
        part = str(part).strip()

        if not part or part in seen:
            continue

        seen.add(part)
        unique.append(part)

    return ", ".join(unique)


# ============================================================
# Extract SEO fields
# ============================================================

def _extract_all_fields(instance):
    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get_for_model(
            instance.__class__
        )
    except Exception:
        logger.exception(
            "SEO ContentType lookup failed for %s",
            instance.__class__.__name__,
        )
        ct = None

    title_fa = _extract_title_smart(
        instance,
        lang="fa",
    )

    title_en = _extract_title_smart(
        instance,
        lang="en",
    )

    description_fa = _extract_description_smart(
        instance,
        lang="fa",
    )

    description_en = _extract_description_smart(
        instance,
        lang="en",
    )

    keywords = _extract_keywords(
        instance,
        title_fa,
        title_en,
    )

    canonical = ""

    get_url = getattr(
        instance,
        "get_absolute_url",
        None,
    )

    if callable(get_url):
        try:
            canonical = get_url() or ""
        except Exception:
            logger.exception(
                "SEO URL extraction failed for %s:%s",
                instance.__class__.__name__,
                instance.pk,
            )

    if not canonical:
        canonical = _get(
            instance,
            "url",
            "canonical",
            default="",
        )

    focus_keyphrase = _get(
        instance,
        "focus_keyphrase",
        "meta_keyphrase",
        "primary_keyword",
        default="",
    )

    if not focus_keyphrase and title_fa:
        focus_keyphrase = " ".join(
            title_fa.split()[:3]
        )

    main_image = _extract_image(
        instance,
        "main_image",
        "image",
        "cover",
        "thumbnail",
        "picture",
        "photo",
        "image_fa",
        "image_en",
        "svg",
    )

    og_title = _get(
        instance,
        "og_title",
        default="",
    )

    og_title_en = _get(
        instance,
        "og_title_en",
        default="",
    )

    og_description = _get(
        instance,
        "og_description",
        default="",
    )

    og_description_en = _get(
        instance,
        "og_description_en",
        default="",
    )

    twitter_title = _get(
        instance,
        "twitter_title",
        default="",
    )

    twitter_title_en = _get(
        instance,
        "twitter_title_en",
        default="",
    )

    twitter_description = _get(
        instance,
        "twitter_description",
        default="",
    )

    twitter_description_en = _get(
        instance,
        "twitter_description_en",
        default="",
    )

    schema_type = _get(
        instance,
        "schema_type",
        default="auto",
    )

    schema_json = _get(
        instance,
        "schema_json",
        default=None,
    )

    breadcrumb_title = _get(
        instance,
        "breadcrumb_title",
        default="",
    )

    breadcrumb_title_en = _get(
        instance,
        "breadcrumb_title_en",
        default="",
    )

    hreflang_group = _get(
        instance,
        "hreflang_group",
        default="",
    )

    if (
        not hreflang_group
        and ct is not None
        and instance.pk
    ):
        hreflang_group = _build_hreflang_group(
            instance,
            ct,
        )

    publish_status = _get(
        instance,
        "publish_status",
        default="published",
    )

    publish_at = _get(
        instance,
        "publish_at",
        "publish_date",
        default=None,
    )

    expire_at = _get(
        instance,
        "expire_at",
        "expire_date",
        default=None,
    )

    index_control = _get(
        instance,
        "index_control",
        default="index",
    )

    follow_control = _get(
        instance,
        "follow_control",
        default="follow",
    )

    return {
        "title": _text(title_fa, 70),
        "title_en": _text(title_en, 70),

        "description": _text(
            description_fa,
            160,
        ),
        "description_en": _text(
            description_en,
            160,
        ),

        "keywords": _text(keywords),

        "canonical": _text(canonical),

        "focus_keyphrase": _text(
            focus_keyphrase,
            120,
        ),

        "og_image": main_image,
        "twitter_image": main_image,

        "og_title": _text(
            og_title or title_fa,
            70,
        ),
        "og_title_en": _text(
            og_title_en or title_en,
            70,
        ),

        "og_description": _text(
            og_description or description_fa,
            160,
        ),
        "og_description_en": _text(
            og_description_en or description_en,
            160,
        ),

        "twitter_title": _text(
            twitter_title or og_title or title_fa,
            70,
        ),
        "twitter_title_en": _text(
            twitter_title_en or og_title_en or title_en,
            70,
        ),

        "twitter_description": _text(
            twitter_description
            or og_description
            or description_fa,
            160,
        ),
        "twitter_description_en": _text(
            twitter_description_en
            or og_description_en
            or description_en,
            160,
        ),

        "schema_type": schema_type or "auto",
        "schema_json": schema_json,

        "breadcrumb_title": _text(
            breadcrumb_title or title_fa,
            120,
        ),
        "breadcrumb_title_en": _text(
            breadcrumb_title_en or title_en,
            120,
        ),

        "hreflang_group": _text(
            hreflang_group
        ),

        "publish_status": (
            publish_status or "published"
        ),
        "publish_at": publish_at,
        "expire_at": expire_at,

        "index_control": (
            index_control or "index"
        ),
        "follow_control": (
            follow_control or "follow"
        ),
    }


# ============================================================
# SEO model helpers
# ============================================================

def _content_type_for_instance(instance):
    from django.contrib.contenttypes.models import ContentType

    ct = ContentType.objects.get_for_model(
        instance.__class__
    )

    content_type = MODEL_TO_CONTENT_TYPE.get(
        (ct.app_label, ct.model)
    )

    return ct, content_type


def _seo_lookup(instance, ct):
    return {
        "app_label": ct.app_label,
        "model_name": ct.model,
        "object_id": instance.pk,
    }


def _valid_seo_fields():
    return {
        field.name
        for field in SEOSetting._meta.concrete_fields
    }


# ============================================================
# Create SEO setting
# ============================================================

def _ensure_seo_setting(instance):
    if not instance.pk:
        return

    try:
        ct, content_type = _content_type_for_instance(
            instance
        )

        if not content_type:
            return

        lookup = _seo_lookup(
            instance,
            ct,
        )

        if SEOSetting.objects.filter(
            **lookup
        ).exists():
            return

        data = _extract_all_fields(instance)

        if not data.get("title"):
            data["title"] = "بدون عنوان"

        if not data.get("og_image"):
            data.pop("og_image", None)

        if not data.get("twitter_image"):
            data.pop("twitter_image", None)

        allowed = _valid_seo_fields()

        data = {
            key: value
            for key, value in data.items()
            if key in allowed
        }

        SEOSetting.objects.get_or_create(
            **lookup,
            defaults={
                "content_type": content_type,
                "is_active": True,
                **data,
            },
        )

    except Exception:
        logger.exception(
            "SEO creation failed for %s:%s",
            instance.__class__.__name__,
            instance.pk,
        )


# ============================================================
# Update SEO setting
# ============================================================

def _update_seo_setting(instance, force=False):
    """
    Ordinary updates fill only empty SEO fields.

    force=True overwrites nonempty fields with nonempty
    values extracted from the source model.
    """

    if not instance.pk:
        return

    try:
        ct, content_type = _content_type_for_instance(
            instance
        )

        if not content_type:
            return

        seo = SEOSetting.objects.filter(
            **_seo_lookup(instance, ct)
        ).first()

        if seo is None:
            return

        data = _extract_all_fields(instance)

        allowed = _valid_seo_fields()

        protected = {
            "id",
            "pk",
            "content_type",
            "app_label",
            "model_name",
            "object_id",
            "is_active",
            "created_at",
            "updated_at",
            "seo_score",
            "publish_status",
            "publish_at",
            "expire_at",
            "index_control",
            "follow_control",
            "robots",
        }

        changed = []

        for field, value in data.items():
            if (
                field not in allowed
                or field in protected
            ):
                continue

            if value is None or value == "" or value == []:
                continue

            current = getattr(
                seo,
                field,
                None,
            )

            if not force and current not in (
                None,
                "",
                [],
            ):
                continue

            if current == value:
                continue

            setattr(
                seo,
                field,
                value,
            )

            changed.append(field)

        if changed:
            seo.save(
                update_fields=changed
            )

    except Exception:
        logger.exception(
            "SEO update failed for %s:%s",
            instance.__class__.__name__,
            instance.pk,
        )


# ============================================================
# Delete SEO setting
# ============================================================

def _delete_seo_setting(instance):
    if not instance.pk:
        return

    try:
        ct, content_type = _content_type_for_instance(
            instance
        )

        if not content_type:
            return

        SEOSetting.objects.filter(
            **_seo_lookup(instance, ct)
        ).delete()

    except Exception:
        logger.exception(
            "SEO deletion failed for %s:%s",
            instance.__class__.__name__,
            instance.pk,
        )


# ============================================================
# Generic signal handlers
# ============================================================

def _generic_post_save(
    sender,
    instance,
    created,
    **kwargs,
):
    if created:
        _ensure_seo_setting(instance)
    else:
        _update_seo_setting(instance)


def _generic_post_delete(
    sender,
    instance,
    **kwargs,
):
    _delete_seo_setting(instance)


# ============================================================
# Lazy signal connections
# ============================================================

def connect_lazy_receivers():
    connected = 0

    for (
        app_label,
        model_name,
    ), content_type in MODEL_TO_CONTENT_TYPE.items():

        try:
            model = apps.get_model(
                app_label,
                model_name,
            )

        except LookupError:
            logger.warning(
                "SEO model not found: %s.%s",
                app_label,
                model_name,
            )
            continue

        if model is None:
            continue

        post_save.connect(
            _generic_post_save,
            sender=model,
            dispatch_uid=(
                f"seo_{app_label}_"
                f"{model_name}_post_save"
            ),
            weak=False,
        )

        post_delete.connect(
            _generic_post_delete,
            sender=model,
            dispatch_uid=(
                f"seo_{app_label}_"
                f"{model_name}_post_delete"
            ),
            weak=False,
        )

        connected += 1

    return connected


def disconnect_lazy_receivers():
    for (
        app_label,
        model_name,
    ), content_type in MODEL_TO_CONTENT_TYPE.items():

        try:
            model = apps.get_model(
                app_label,
                model_name,
            )
        except LookupError:
            continue

        if model is None:
            continue

        post_save.disconnect(
            sender=model,
            dispatch_uid=(
                f"seo_{app_label}_"
                f"{model_name}_post_save"
            ),
        )

        post_delete.disconnect(
            sender=model,
            dispatch_uid=(
                f"seo_{app_label}_"
                f"{model_name}_post_delete"
            ),
        )
