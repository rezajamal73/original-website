
"""
SEO Administration
Parsa Novin Kavosh
Django 6 compatible

Features:
- SEO settings management
- Real content names in analysis history
- SEO score display
- Google, Twitter and OG previews
- SEO reanalysis, resync and rebuild
- Audit logging
"""

import logging
from urllib.parse import urlsplit

from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.http import url_has_allowed_host_and_scheme

from .audit import (
    record_seo_success,
    record_seo_failure,
    record_seo_denied,
)
from .forms import SEOSettingAdminForm
from .models import SEOSetting, SEODefault, SEOAnalysisLog


logger = logging.getLogger(__name__)


# ==========================================================
# HELPERS
# ==========================================================

def _score_color(score):
    try:
        score = int(score)
    except (TypeError, ValueError):
        return "#6c757d"

    if score >= 70:
        return "#198754"
    if score >= 40:
        return "#ffc107"
    return "#dc3545"


def _score_label(score):
    try:
        score = int(score)
    except (TypeError, ValueError):
        return "بدون امتیاز"

    if score >= 70:
        return "خوب"
    if score >= 40:
        return "قابل بهبود"
    return "ضعیف"


def _short(value, limit=60):
    value = str(value or "").strip()

    if len(value) > limit:
        return value[:limit] + "…"

    return value


def _safe_image_url(value):
    if not value:
        return ""

    url = str(value).strip()

    if (
        not url
        or url.startswith("//")
        or "\\" in url
        or any(ord(char) < 32 for char in url)
    ):
        return ""

    if url.startswith("/"):
        return url

    if not url.lower().startswith("https://"):
        return ""

    allowed_hosts = (
        set(settings.ALLOWED_HOSTS) - {"*"}
    )

    if not url_has_allowed_host_and_scheme(
        url,
        allowed_hosts=allowed_hosts,
        require_https=True,
    ):
        return ""

    return url


# ==========================================================
# REAL CONTENT NAME RESOLVER
# ==========================================================

CONTENT_LABELS = {
    "product": "محصول",
    "person": "شخص",
    "resume": "رزومه",
    "companycatalog": "کاتالوگ شرکت",
    "blog": "مقاله",
    "news": "خبر",
    "banner": "بنر",
    "catalog": "کاتالوگ",
}


def _get_related_content(seo):
    """
    Find the actual object referenced by an SEO record.

    No database records are modified.
    """
    if seo is None:
        return None

    app_label = getattr(seo, "app_label", None)
    model_name = getattr(seo, "model_name", None)
    object_id = getattr(seo, "object_id", None)

    if (
        not app_label
        or not model_name
        or object_id is None
    ):
        return None

    try:
        model = apps.get_model(
            app_label,
            model_name,
        )

        if model is None:
            return None

        return model._default_manager.filter(
            pk=object_id
        ).first()

    except Exception:
        logger.exception(
            "SEO related content lookup failed: %s",
            getattr(seo, "pk", None),
        )
        return None


def _real_content_name(seo):
    """
    Resolve a readable name for SEO records.

    Priority:
    1. Related object's real title/name
    2. SEO title
    3. Page key
    4. Readable type and identifier
    """
    if seo is None:
        return "محتوای نامشخص"

    related = _get_related_content(seo)

    if related is not None:
        candidate_fields = (
            "title",
            "title_fa",
            "name",
            "full_name",
            "name_fa",
            "product_name",
            "person_name",
            "first_name",
            "subject",
            "heading",
            "caption",
        )

        for field in candidate_fields:
            try:
                value = getattr(related, field, None)

                if callable(value):
                    continue

                if value is not None:
                    value = str(value).strip()

                    if value:
                        if field == "first_name":
                            last_name = str(
                                getattr(
                                    related,
                                    "last_name",
                                    "",
                                ) or ""
                            ).strip()

                            value = (
                                f"{value} {last_name}"
                            ).strip()

                        return value

            except Exception:
                continue

        try:
            value = str(related).strip()

            if (
                value
                and not value.startswith(
                    related.__class__.__name__
                    + " object"
                )
            ):
                return value
        except Exception:
            pass

    for field in (
        "title",
        "title_en",
        "page_key",
    ):
        value = getattr(seo, field, None)

        if value:
            return str(value).strip()

    model_name = str(
        getattr(seo, "model_name", "") or ""
    ).lower()

    content_type = str(
        getattr(seo, "content_type", "") or ""
    ).lower()

    label = CONTENT_LABELS.get(
        model_name,
        CONTENT_LABELS.get(
            content_type,
            model_name or content_type or "محتوا",
        ),
    )

    object_id = getattr(
        seo,
        "object_id",
        None,
    )

    if object_id is not None:
        return f"{label} شماره {object_id}"

    return f"تنظیم SEO شماره {seo.pk}"


# ==========================================================
# SEO FORM
# ==========================================================

class CompatibleSEOSettingAdminForm(SEOSettingAdminForm):

    def clean(self):
        cleaned_data = super().clean()

        publish_at = cleaned_data.get("publish_at")
        expire_at = cleaned_data.get("expire_at")

        if (
            publish_at is not None
            and expire_at is not None
            and expire_at <= publish_at
        ):
            self.add_error(
                "expire_at",
                "تاریخ انقضا باید بعد از تاریخ انتشار باشد.",
            )

        content_type = cleaned_data.get("content_type")

        page_key = (
            cleaned_data.get("page_key") or ""
        ).strip()

        app_label = (
            cleaned_data.get("app_label") or ""
        ).strip()

        model_name = (
            cleaned_data.get("model_name") or ""
        ).strip()

        object_id = cleaned_data.get("object_id")

        original = None

        if self.instance.pk:
            original = SEOSetting.objects.filter(
                pk=self.instance.pk
            ).first()

        identity_changed = original is None

        if original is not None:
            identity_changed = any((
                original.content_type != content_type,
                (original.page_key or "") != page_key,
                (original.app_label or "") != app_label,
                (original.model_name or "") != model_name,
                original.object_id != object_id,
            ))

        if identity_changed:
            if content_type == "page" and not page_key:
                self.add_error(
                    "page_key",
                    "برای صفحه ثابت، کلید صفحه الزامی است.",
                )

            has_reference = (
                bool(app_label)
                or bool(model_name)
                or object_id is not None
            )

            if has_reference:
                if not app_label:
                    self.add_error(
                        "app_label",
                        "نام اپلیکیشن را وارد کنید.",
                    )

                if not model_name:
                    self.add_error(
                        "model_name",
                        "نام مدل را وارد کنید.",
                    )

                if object_id is None:
                    self.add_error(
                        "object_id",
                        "شناسه محتوای مرتبط را وارد کنید.",
                    )

        if (
            app_label
            and model_name
            and object_id is not None
        ):
            duplicates = SEOSetting.objects.filter(
                app_label=app_label,
                model_name=model_name,
                object_id=object_id,
            )

            if self.instance.pk:
                duplicates = duplicates.exclude(
                    pk=self.instance.pk
                )

            if duplicates.exists():
                self.add_error(
                    "object_id",
                    "برای این محتوا قبلاً SEO ثبت شده است.",
                )

        if content_type == "page" and page_key:
            duplicates = SEOSetting.objects.filter(
                content_type="page",
                page_key=page_key,
            )

            if self.instance.pk:
                duplicates = duplicates.exclude(
                    pk=self.instance.pk
                )

            if duplicates.exists():
                self.add_error(
                    "page_key",
                    "این کلید صفحه قبلاً ثبت شده است.",
                )

        return cleaned_data


# ==========================================================
# ANALYSIS INLINE
# ==========================================================

class SEOAnalysisLogInline(admin.TabularInline):
    model = SEOAnalysisLog
    extra = 0

    readonly_fields = (
        "score",
        "checks",
        "created_at",
    )

    can_delete = False
    max_num = 5

    def has_add_permission(self, request, obj=None):
        return False


# ==========================================================
# SEO SETTINGS ADMIN
# ==========================================================

@admin.register(SEOSetting)
class SEOSettingAdmin(admin.ModelAdmin):

    form = CompatibleSEOSettingAdminForm
    change_form_template = "seo/change_form.html"

    list_display = (
        "title_short",
        "content_type_badge",
        "page_key",
        "app_label",
        "model_name",
        "object_id",
        "score_badge",
        "status_badge",
        "updated_at",
        "delete_action",
    )

    list_display_links = ("title_short",)

    list_filter = (
        "content_type",
        "is_active",
        "publish_status",
        "index_control",
        "app_label",
    )

    search_fields = (
        "title",
        "title_en",
        "description",
        "description_en",
        "keywords",
        "focus_keyphrase",
        "page_key",
        "app_label",
        "model_name",
        "object_id",
    )

    ordering = ("-updated_at",)
    list_per_page = 50

    readonly_fields = (
        "created_at",
        "updated_at",
        "seo_score",
        "score_badge_large",
        "google_preview",
        "twitter_preview",
        "breadcrumb_preview",
        "og_preview",
        "focus_keyphrase_hint",
    )

    inlines = (SEOAnalysisLogInline,)

    fieldsets = (
        (
            "📌 اتصال و مشخصات محتوا",
            {
                "fields": (
                    "content_type",
                    "page_key",
                    "app_label",
                    "model_name",
                    "object_id",
                    "url",
                    "is_active",
                ),
            },
        ),
        (
            "🎯 عبارت کلیدی اصلی",
            {
                "fields": (
                    "focus_keyphrase",
                    "focus_keyphrase_hint",
                    "seo_score",
                    "score_badge_large",
                ),
            },
        ),
        (
            "🔍 تنظیمات موتور جستجو",
            {
                "fields": (
                    "title",
                    "title_en",
                    "description",
                    "description_en",
                    "keywords",
                    "canonical",
                ),
            },
        ),
        (
            "🤖 کنترل ایندکس",
            {
                "fields": (
                    "index_control",
                    "follow_control",
                    "robots",
                ),
            },
        ),
        (
            "🌐 شبکه‌های اجتماعی",
            {
                "fields": (
                    "og_title",
                    "og_title_en",
                    "og_description",
                    "og_description_en",
                    "og_type",
                    "og_image",
                    "og_preview",
                ),
            },
        ),
        (
            "🐦 کارت توییتر",
            {
                "fields": (
                    "twitter_card",
                    "twitter_title",
                    "twitter_title_en",
                    "twitter_description",
                    "twitter_description_en",
                    "twitter_image",
                    "twitter_preview",
                ),
            },
        ),
        (
            "🧩 اطلاعات ساختاریافته گوگل",
            {
                "fields": (
                    "schema_type",
                    "schema_json",
                ),
            },
        ),
        (
            "🍞 Breadcrumb",
            {
                "fields": (
                    "breadcrumb_title",
                    "breadcrumb_title_en",
                    "breadcrumb_preview",
                ),
            },
        ),
        (
            "🌍 Hreflang",
            {
                "fields": ("hreflang_group",),
            },
        ),
        (
            "🕒 زمان‌بندی انتشار",
            {
                "fields": (
                    "publish_status",
                    "publish_at",
                    "expire_at",
                ),
            },
        ),
        (
            "👁 پیش‌نمایش گوگل",
            {
                "fields": ("google_preview",),
            },
        ),
        (
            "🕓 اطلاعات سیستمی",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    # ======================================================
    # CUSTOM SEO ACTIONS
    # ======================================================

    CUSTOM_ACTIONS = {
        "_reanalyze_seo": "reanalyze",
        "_resync_seo": "resync",
        "_rebuild_seo": "rebuild",
    }

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        if request.method == "POST":
            requested = [
                name
                for name in self.CUSTOM_ACTIONS
                if name in request.POST
            ]

            if requested:
                if len(requested) != 1:
                    return HttpResponseForbidden(
                        "درخواست عملیات SEO نامعتبر است."
                    )

                if object_id is None:
                    return HttpResponseForbidden(
                        "ابتدا رکورد SEO را ذخیره کنید."
                    )

                obj = self.get_object(
                    request,
                    object_id,
                )

                if obj is None:
                    return HttpResponseForbidden(
                        "رکورد SEO یافت نشد."
                    )

                action = self.CUSTOM_ACTIONS[
                    requested[0]
                ]

                if not self.has_change_permission(
                    request,
                    obj,
                ):
                    record_seo_denied(
                        request,
                        obj,
                        action,
                        "کاربر مجوز ویرایش ندارد.",
                    )

                    return HttpResponseForbidden(
                        "مجوز ویرایش این رکورد را ندارید."
                    )

                if (
                    action == "rebuild"
                    and not request.user.is_superuser
                ):
                    record_seo_denied(
                        request,
                        obj,
                        action,
                        "بازسازی توسط کاربر غیرمدیر ارشد.",
                    )

                    return HttpResponseForbidden(
                        "بازسازی فقط برای مدیر ارشد مجاز است."
                    )

                return self._execute_action(
                    request,
                    obj,
                    action,
                )

        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    def _execute_action(self, request, obj, action):
        if action == "reanalyze":
            return self._reanalyze(request, obj)

        if action == "resync":
            return self._resync(request, obj)

        if action == "rebuild":
            return self._rebuild(request, obj)

        return HttpResponseForbidden(
            "عملیات SEO ناشناخته است."
        )

    def _reanalyze(self, request, obj):
        try:
            from .analyzer import analyze_and_save

            related_object = _get_related_content(obj)

            result = analyze_and_save(
                obj,
                obj=related_object,
            )

            if (
                not isinstance(result, dict)
                or "score" not in result
            ):
                raise ValueError(
                    "Analyzer did not return a score."
                )

            recorded = record_seo_success(
                request,
                obj,
                "reanalyze",
                f"امتیاز: {result['score']}",
            )

            messages.success(
                request,
                "✅ تحلیل مجدد انجام شد. "
                f"امتیاز: {result['score']} / 100",
            )

            if not recorded:
                messages.warning(
                    request,
                    "گزارش فعالیت ثبت نشد.",
                )

        except Exception:
            logger.exception(
                "SEO reanalysis failed: %s",
                obj.pk,
            )

            record_seo_failure(
                request,
                obj,
                "reanalyze",
                "خطا هنگام تحلیل مجدد.",
            )

            messages.error(
                request,
                "❌ تحلیل مجدد ناموفق بود.",
            )

        return redirect(request.path)

    def _resync(self, request, obj):
        related_object = _get_related_content(obj)

        if related_object is None:
            record_seo_failure(
                request,
                obj,
                "resync",
                "محتوای مرتبط پیدا نشد.",
            )

            messages.warning(
                request,
                "⚠️ محتوای مرتبط پیدا نشد.",
            )

            return redirect(request.path)

        try:
            from .signals import _update_seo_setting

            _update_seo_setting(related_object)

            recorded = record_seo_success(
                request,
                obj,
                "resync",
                "تابع همگام‌سازی اجرا شد.",
            )

            messages.success(
                request,
                "✅ همگام‌سازی اجرا شد.",
            )

            if not recorded:
                messages.warning(
                    request,
                    "گزارش فعالیت ثبت نشد.",
                )

        except Exception:
            logger.exception(
                "SEO resync failed: %s",
                obj.pk,
            )

            record_seo_failure(
                request,
                obj,
                "resync",
                "خطا هنگام همگام‌سازی.",
            )

            messages.error(
                request,
                "❌ همگام‌سازی ناموفق بود.",
            )

        return redirect(request.path)

    def _rebuild(self, request, obj):
        if not request.user.is_superuser:
            record_seo_denied(
                request,
                obj,
                "rebuild",
                "مجوز مدیر ارشد وجود ندارد.",
            )

            return HttpResponseForbidden(
                "بازسازی فقط برای مدیر ارشد مجاز است."
            )

        related_object = _get_related_content(obj)

        if related_object is None:
            record_seo_failure(
                request,
                obj,
                "rebuild",
                "محتوای مرتبط پیدا نشد.",
            )

            messages.warning(
                request,
                "⚠️ محتوای مرتبط پیدا نشد.",
            )

            return redirect(request.path)

        try:
            from .signals import _extract_all_fields

            data = _extract_all_fields(related_object)

            if not isinstance(data, dict):
                raise ValueError(
                    "Invalid SEO extraction result."
                )

            if not data.get("og_image"):
                data.pop("og_image", None)

            if not data.get("twitter_image"):
                data.pop("twitter_image", None)

            valid_fields = {
                field.name
                for field in obj._meta.concrete_fields
            }

            protected_fields = {
                "id",
                "pk",
                "created_at",
                "updated_at",
                "content_type",
                "page_key",
                "app_label",
                "model_name",
                "object_id",
                "is_active",
                "seo_score",
            }

            with transaction.atomic():
                current = (
                    SEOSetting.objects
                    .select_for_update()
                    .get(pk=obj.pk)
                )

                for field, value in data.items():
                    if (
                        field in valid_fields
                        and field not in protected_fields
                    ):
                        setattr(current, field, value)

                if not current.title:
                    current.title = "بدون عنوان"

                current.save()

            recorded = record_seo_success(
                request,
                current,
                "rebuild",
                "اطلاعات از محتوای مرتبط بازسازی شد.",
            )

            messages.success(
                request,
                "♻️ بازسازی کامل SEO انجام شد.",
            )

            if not recorded:
                messages.warning(
                    request,
                    "بازسازی انجام شد، اما گزارش ثبت نشد.",
                )

            try:
                from .analyzer import analyze_and_save

                current.refresh_from_db()

                analyze_and_save(
                    current,
                    obj=related_object,
                )

            except Exception:
                logger.exception(
                    "SEO analysis after rebuild failed: %s",
                    obj.pk,
                )

                messages.warning(
                    request,
                    "بازسازی انجام شد، اما تحلیل SEO ناموفق بود.",
                )

        except Exception:
            logger.exception(
                "SEO rebuild failed: %s",
                obj.pk,
            )

            record_seo_failure(
                request,
                obj,
                "rebuild",
                "خطا هنگام بازسازی.",
            )

            messages.error(
                request,
                "❌ بازسازی SEO ناموفق بود.",
            )

        return redirect(request.path)

    # ======================================================
    # LIST DISPLAY
    # ======================================================

    @admin.display(
        description="عنوان",
        ordering="title",
    )
    def title_short(self, obj):
        return _short(
            _real_content_name(obj),
            65,
        )

    @admin.display(description="نوع محتوا")
    def content_type_badge(self, obj):
        return obj.get_content_type_display()

    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color:#198754;'
                'font-weight:bold;">{}</span>',
                "● فعال",
            )

        return format_html(
            '<span style="color:#dc3545;'
            'font-weight:bold;">{}</span>',
            "● غیرفعال",
        )

    @admin.display(
        description="امتیاز SEO",
        ordering="seo_score",
    )
    def score_badge(self, obj):
        score = obj.seo_score or 0

        return format_html(
            '<span style="background:{};'
            'color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">'
            '{} / 100 – {}</span>',
            _score_color(score),
            score,
            _score_label(score),
        )

    @admin.display(description="امتیاز کلی SEO")
    def score_badge_large(self, obj):
        score = obj.seo_score or 0

        return format_html(
            '<div style="display:inline-block;'
            'padding:10px 18px;background:{};'
            'color:#fff;border-radius:12px;'
            'font-size:16px;font-weight:bold;">'
            '{} / 100 — {}</div>',
            _score_color(score),
            score,
            _score_label(score),
        )

    # ======================================================
    # PREVIEWS
    # ======================================================

    @admin.display(description="راهنما")
    def focus_keyphrase_hint(self, obj):
        return format_html(
            '<div style="background:#f0f6fc;'
            'border-left:4px solid #2271b1;'
            'padding:8px 12px;border-radius:6px;'
            'font-size:12px;color:#1d2327;">'
            '{}</div>',
            (
                "🔎 عبارت کلیدی اصلی را با عنوان، "
                "توضیحات و محتوای صفحه هماهنگ کنید."
            ),
        )

    @admin.display(description="پیش‌نمایش در گوگل")
    def google_preview(self, obj):
        title = (
            obj.title_en
            or obj.title
            or _real_content_name(obj)
        )

        description = (
            obj.description_en
            or obj.description
            or "توضیحات SEO ..."
        )

        url = (
            obj.canonical
            or obj.url
            or "https://nkavosh.com/"
        )

        try:
            host = urlsplit(str(url)).hostname
        except ValueError:
            host = None

        host = host or "nkavosh.com"

        return format_html(
            '<div style="max-width:600px;'
            'padding:14px 16px;'
            'border:1px solid #dadce0;'
            'border-radius:10px;background:#fff;">'
            '<div style="color:#202124;'
            'font-size:13px;">{}</div>'
            '<div style="color:#5f6368;'
            'font-size:11px;margin:5px 0;">{}</div>'
            '<div style="color:#1a0dab;'
            'font-size:18px;">{}</div>'
            '<div style="color:#4d5156;'
            'font-size:13px;">{}</div>'
            '</div>',
            host,
            url,
            _short(title, 60),
            _short(description, 160),
        )

    @admin.display(description="پیش‌نمایش کارت توییتر")
    def twitter_preview(self, obj):
        title = (
            obj.twitter_title_en
            or obj.twitter_title
            or obj.og_title_en
            or obj.og_title
            or obj.title_en
            or obj.title
            or "عنوان توییتر"
        )

        description = (
            obj.twitter_description_en
            or obj.twitter_description
            or obj.og_description_en
            or obj.og_description
            or obj.description_en
            or obj.description
            or "توضیحات توییتر ..."
        )

        image_url = ""

        for image_field in (
            obj.twitter_image,
            obj.og_image,
        ):
            if not image_field:
                continue

            try:
                image_url = _safe_image_url(
                    image_field.url
                )
            except (ValueError, OSError):
                image_url = ""

            if image_url:
                break

        if image_url:
            image_block = format_html(
                '<img src="{}" alt="Twitter preview" '
                'loading="lazy" '
                'style="width:100%;height:180px;'
                'object-fit:cover;display:block;">',
                image_url,
            )
        else:
            image_block = format_html(
                '<div style="height:180px;'
                'background:#e8f0fe;'
                'display:flex;align-items:center;'
                'justify-content:center;">'
                '{}</div>',
                "بدون تصویر",
            )

        return format_html(
            '<div style="max-width:520px;'
            'border:1px solid #e1e8ed;'
            'border-radius:10px;overflow:hidden;">'
            '{}'
            '<div style="padding:12px 14px;">'
            '<strong>{}</strong>'
            '<div style="font-size:13px;'
            'margin-top:5px;">{}</div>'
            '</div></div>',
            image_block,
            title,
            description,
        )

    @admin.display(description="پیش‌نمایش Breadcrumb")
    def breadcrumb_preview(self, obj):
        items = ["خانه"]

        if obj.content_type != "page":
            items.append(
                obj.get_content_type_display()
            )

        items.append(
            obj.breadcrumb_title_en
            or obj.breadcrumb_title
            or _real_content_name(obj)
        )

        html_items = []

        for index, item in enumerate(items):
            is_last = index == len(items) - 1

            html_items.append(
                format_html(
                    '<span style="color:{};'
                    'font-weight:{};">{}</span>',
                    "#202124" if is_last else "#1a73e8",
                    "bold" if is_last else "normal",
                    item,
                )
            )

            if not is_last:
                html_items.append(
                    format_html(
                        '<span style="margin:0 6px;">'
                        '{}</span>',
                        "›",
                    )
                )

        content = format_html_join(
            "",
            "{}",
            ((item,) for item in html_items),
        )

        return format_html(
            '<div style="padding:10px 14px;'
            'background:#f8f9fa;'
            'border-radius:8px;">{}</div>',
            content,
        )

    @admin.display(description="پیش‌نمایش تصویر OG")
    def og_preview(self, obj):
        if not obj.og_image:
            return "تصویری انتخاب نشده"

        try:
            image_url = _safe_image_url(
                obj.og_image.url
            )

            if not image_url:
                return "آدرس تصویر معتبر نیست"

            return format_html(
                '<img src="{}" '
                'alt="Open Graph preview" '
                'loading="lazy" '
                'style="max-width:350px;'
                'height:auto;border-radius:8px;">',
                image_url,
            )

        except (ValueError, OSError):
            logger.exception(
                "OG image preview error"
            )
            return "خطا در بارگذاری تصویر"

    @admin.display(description="حذف")
    def delete_action(self, obj):
        if not obj or not obj.pk:
            return "—"

        try:
            url = reverse(
                "admin:app_seo_seosetting_delete",
                args=[obj.pk],
            )

            return format_html(
                '<a href="{}" '
                'style="color:#dc3545;'
                'font-weight:bold;">'
                '🗑 حذف</a>',
                url,
            )

        except Exception:
            logger.exception(
                "SEO delete link error"
            )
            return "—"


# ==========================================================
# SEO DEFAULT ADMIN
# ==========================================================

@admin.register(SEODefault)
class SEODefaultAdmin(admin.ModelAdmin):

    list_display = (
        "language",
        "content_type",
        "title_template_short",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "language",
        "content_type",
        "is_active",
    )

    search_fields = (
        "title_template",
        "description_template",
    )

    fieldsets = (
        (
            "📌 زبان و نوع محتوا",
            {
                "fields": (
                    "language",
                    "content_type",
                    "is_active",
                ),
            },
        ),
        (
            "🧩 الگوها",
            {
                "description": (
                    "می‌توانید از متغیرهای "
                    "{title} و {site} استفاده کنید."
                ),
                "fields": (
                    "title_template",
                    "description_template",
                ),
            },
        ),
        (
            "🌐 پیش‌فرض‌های شبکه‌های اجتماعی",
            {
                "fields": (
                    "default_og_image",
                    "default_schema_type",
                ),
            },
        ),
        (
            "🕓 اطلاعات سیستمی",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(description="الگوی عنوان")
    def title_template_short(self, obj):
        if not obj.title_template:
            return "—"

        return _short(obj.title_template, 50)


# ==========================================================
# SEO ANALYSIS LOG ADMIN
# ==========================================================

@admin.register(SEOAnalysisLog)
class SEOAnalysisLogAdmin(admin.ModelAdmin):

    list_display = (
        "content_name",
        "score_badge",
        "created_at",
    )

    list_display_links = (
        "content_name",
    )

    list_select_related = (
        "seo_setting",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "seo_setting__title",
        "seo_setting__title_en",
        "seo_setting__page_key",
        "seo_setting__model_name",
        "seo_setting__app_label",
    )

    readonly_fields = (
        "seo_setting",
        "score",
        "checks",
        "created_at",
    )

    ordering = ("-created_at",)
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    @admin.display(description="نام واقعی محتوا")
    def content_name(self, obj):
        seo = obj.seo_setting

        if seo is None:
            return "محتوای نامشخص"

        name = _real_content_name(seo)

        model_name = str(
            getattr(seo, "model_name", "") or ""
        ).lower()

        content_type = str(
            getattr(seo, "content_type", "") or ""
        ).lower()

        label = CONTENT_LABELS.get(
            model_name,
            CONTENT_LABELS.get(
                content_type,
                "محتوا",
            ),
        )

        return format_html(
            '<div style="line-height:1.6;">'
            '<strong>{}</strong>'
            '<div style="color:#6c757d;'
            'font-size:11px;">{}</div>'
            '</div>',
            _short(name, 85),
            label,
        )

    @admin.display(description="امتیاز")
    def score_badge(self, obj):
        return format_html(
            '<span style="background:{};'
            'color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">'
            '{} / 100</span>',
            _score_color(obj.score),
            obj.score,
        )


# ==========================================================
# ADMIN TITLES
# ==========================================================

admin.site.site_header = "🚀 پنل مدیریت SEO"
admin.site.site_title = "SEO Admin"
admin.site.index_title = "مدیریت سئو و بهینه‌سازی"
