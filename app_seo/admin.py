# app_seo/admin.py

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html, mark_safe

from .models import SEOSetting, SEODefault, SEOAnalysisLog


# =====================================================
#  کمک‌تابع‌های نمایش
# =====================================================

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


def _safe(html):
    """
    اگر HTML رشته بود، mark_safe کن.
    """
    if html is None:
        return ""
    return mark_safe(str(html))


# =====================================================
#  Inline برای تحلیل‌ها
# =====================================================

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


# =====================================================
#  SEOSetting Admin
# =====================================================

@admin.register(SEOSetting)
class SEOSettingAdmin(admin.ModelAdmin):

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
        "description",
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
                "description": (
                    "مشخص کنید این تنظیمات SEO برای کدام صفحه، "
                    "محصول یا محتوای سایت است."
                ),
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
            "🎯 عبارت کلیدی اصلی (Yoast Focus Keyphrase)",
            {
                "description": (
                    "عبارتی که می‌خواهید این صفحه برای آن رتبه بگیرد. "
                    "تحلیل‌گر Yoast بر اساس این عبارت امتیاز می‌دهد."
                ),
                "fields": (
                    "focus_keyphrase",
                    "focus_keyphrase_hint",
                    "seo_score",
                    "score_badge_large",
                ),
            },
        ),

        (
            "🔍 تنظیمات اصلی موتور جستجو (Meta SEO)",
            {
                "description": (
                    "اطلاعاتی که موتورهای جستجو مانند گوگل "
                    "برای نمایش صفحه استفاده می‌کنند."
                ),
                "fields": (
                    "title",
                    "description",
                    "keywords",
                    "canonical",
                ),
            },
        ),

        (
            "🤖 کنترل ایندکس (Robots)",
            {
                "description": (
                    "کنترل دقیق رفتار موتورهای جستجو با این صفحه. "
                    "فیلد Robots قدیمی برای سازگاری حفظ شده است."
                ),
                "fields": (
                    "index_control",
                    "follow_control",
                    "robots",
                ),
            },
        ),

        (
            "🌐 شبکه‌های اجتماعی (Open Graph)",
            {
                "description": (
                    "اطلاعات نمایش صفحه هنگام اشتراک‌گذاری "
                    "در شبکه‌های اجتماعی."
                ),
                "fields": (
                    "og_title",
                    "og_description",
                    "og_type",
                    "og_image",
                    "og_preview",
                ),
            },
        ),

        (
            "🐦 کارت توییتر (Twitter Card)",
            {
                "fields": (
                    "twitter_card",
                    "twitter_title",
                    "twitter_description",
                    "twitter_image",
                    "twitter_preview",
                ),
            },
        ),

        (
            "🧩 اطلاعات ساختاریافته گوگل (Schema JSON-LD)",
            {
                "description": (
                    "در حالت خودکار، نوع Schema بر اساس نوع محتوا "
                    "انتخاب می‌شود. اگر می‌خواهید دستی وارد کنید، "
                    "فیلد JSON را پر کنید."
                ),
                "fields": (
                    "schema_type",
                    "schema_json",
                ),
            },
        ),

        (
            "🍞 Breadcrumb",
            {
                "description": (
                    "عنوان نمایش داده شده در مسیر ناوبری. "
                    "اگر خالی بماند، از عنوان SEO استفاده می‌شود."
                ),
                "fields": (
                    "breadcrumb_title",
                    "breadcrumb_preview",
                ),
            },
        ),

        (
            "🌍 Hreflang (چندزبانه)",
            {
                "description": (
                    "اگر این صفحه نسخه انگلیسی/فارسی دارد، "
                    "یک شناسه مشترک وارد کنید تا به‌صورت "
                    "alternate در سر صفحه ثبت شود."
                ),
                "fields": (
                    "hreflang_group",
                ),
            },
        ),

        (
            "🕒 زمان‌بندی و وضعیت انتشار",
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
                "fields": (
                    "google_preview",
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

    # =================================================
    #  نمایش‌ها
    # =================================================

    @admin.display(description="عنوان", ordering="title")
    def title_short(self, obj):
        if obj.title:
            return obj.title[:60] + ("…" if len(obj.title) > 60 else "")
        return f"— {obj.page_key or obj.object_id or '—'}"

    @admin.display(description="نوع محتوا")
    def content_type_badge(self, obj):
        return obj.get_content_type_display()

    # ✅ اصلاح‌شده: mark_safe به‌جای format_html بدون آرگومان
    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="color:#198754;font-weight:bold;">● فعال</span>'
            )
        return mark_safe(
            '<span style="color:#dc3545;font-weight:bold;">● غیرفعال</span>'
        )

    @admin.display(description="امتیاز SEO", ordering="seo_score")
    def score_badge(self, obj):

        score = obj.seo_score or 0
        color = _score_color(score)
        label = _score_label(score)

        return format_html(
            '<span style="background:{};color:#fff;'
            'padding:2px 8px;border-radius:10px;font-size:11px;">'
            '{} / 100 – {}</span>',
            color, score, label,
        )

    @admin.display(description="امتیاز کلی SEO")
    def score_badge_large(self, obj):

        score = obj.seo_score or 0
        color = _score_color(score)
        label = _score_label(score)

        return format_html(
            '<div style="display:inline-block;padding:10px 18px;'
            'background:{};color:#fff;border-radius:12px;'
            'font-size:16px;font-weight:bold;">'
            '{} / 100 &nbsp;—&nbsp; {}</div>',
            color, score, label,
        )

    @admin.display(description="راهنما")
    def focus_keyphrase_hint(self, obj):
        return mark_safe(
            "<div style='background:#f0f6fc;border-left:4px solid #2271b1;"
            "padding:8px 12px;border-radius:6px;font-size:12px;color:#1d2327;'>"
            "🔎 عبارت کلیدی باید در عنوان، توضیحات، URL و H1 تکرار شود. "
            "طول مناسب: ۲ تا ۴ کلمه. برای هر صفحه فقط یک عبارت اصلی."
            "</div>"
        )

    @admin.display(description="پیش‌نمایش در گوگل")
    def google_preview(self, obj):

        title = obj.title or "عنوان SEO"
        description = obj.description or "توضیحات SEO ..."
        url = obj.canonical or obj.url or "https://example.com/"

        title = title[:60] + ("…" if len(title) > 60 else "")
        description = description[:160] + ("…" if len(description) > 160 else "")

        return format_html(
            '<div style="max-width:600px;padding:14px 16px;'
            'border:1px solid #dadce0;border-radius:10px;'
            'background:#fff;font-family:Arial,sans-serif;">'

            '<div style="display:flex;align-items:center;gap:8px;'
            'margin-bottom:6px;">'
            '<div style="width:26px;height:26px;border-radius:50%;'
            'background:#e8f0fe;display:flex;align-items:center;'
            'justify-content:center;font-size:13px;color:#1a73e8;">'
            '🌐</div>'
            '<div style="display:flex;flex-direction:column;line-height:1.2;">'
            '<span style="color:#202124;font-size:13px;">example.com</span>'
            '<span style="color:#5f6368;font-size:11px;">{}</span>'
            '</div></div>'

            '<div style="color:#1a0dab;font-size:18px;line-height:1.3;'
            'margin:4px 0;">{}</div>'

            '<div style="color:#4d5156;font-size:13px;line-height:1.5;">'
            '{}</div>'

            '</div>',

            url,
            title,
            description,
        )

    @admin.display(description="پیش‌نمایش کارت توییتر")
    def twitter_preview(self, obj):

        title = obj.twitter_title or obj.og_title or obj.title or "عنوان توییتر"
        description = (
            obj.twitter_description
            or obj.og_description
            or obj.description
            or "توضیحات توییتر ..."
        )

        image_url = ""

        if obj.twitter_image:
            try:
                image_url = obj.twitter_image.url
            except Exception:
                image_url = ""

        if not image_url and obj.og_image:
            try:
                image_url = obj.og_image.url
            except Exception:
                image_url = ""

        if image_url:
            image_block = format_html(
                '<div style="width:100%;height:180px;'
                'background-image:url({});'
                'background-size:cover;background-position:center;'
                'border-radius:10px 10px 0 0;"></div>',
                image_url,
            )
        else:
            image_block = mark_safe(
                '<div style="width:100%;height:180px;'
                'background:#e8f0fe;display:flex;align-items:center;'
                'justify-content:center;color:#5f6368;font-size:13px;'
                'border-radius:10px 10px 0 0;">بدون تصویر</div>'
            )

        return format_html(
            '<div style="max-width:520px;border:1px solid #e1e8ed;'
            'border-radius:10px;overflow:hidden;'
            'background:#fff;font-family:Arial,sans-serif;">'

            '{}'

            '<div style="padding:12px 14px;">'
            '<div style="color:#0f1419;font-size:15px;'
            'font-weight:bold;margin-bottom:4px;">{}</div>'
            '<div style="color:#536471;font-size:13px;line-height:1.4;">'
            '{}</div>'
            '<div style="color:#8899a6;font-size:12px;margin-top:8px;">'
            'twitter.com</div>'
            '</div>'

            '</div>',

            image_block,
            title,
            description,
        )

    @admin.display(description="پیش‌نمایش Breadcrumb")
    def breadcrumb_preview(self, obj):

        items = ["خانه"]

        if obj.content_type != "page":
            items.append(obj.get_content_type_display())

        items.append(obj.breadcrumb_title or obj.title or "—")

        html_items = []

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)

            style = (
                "color:#202124;font-weight:bold;"
                if is_last else
                "color:#1a73e8;"
            )

            html_items.append(
                f'<span style="{style}font-size:13px;">{item}</span>'
            )

            if not is_last:
                html_items.append(
                    '<span style="color:#5f6368;margin:0 6px;">›</span>'
                )

        return format_html(
            '<div style="padding:10px 14px;background:#f8f9fa;'
            'border-radius:8px;border:1px solid #dadce0;">{}</div>',
            mark_safe("".join(html_items)),
        )

    @admin.display(description="پیش‌نمایش تصویر OG")
    def og_preview(self, obj):
        if obj.og_image:
            try:
                return format_html(
                    '<img src="{}" style="max-width:350px;'
                    'border-radius:8px;border:1px solid #ddd;">',
                    obj.og_image.url,
                )
            except Exception:
                return "خطا در بارگذاری تصویر"

        return "تصویری انتخاب نشده"

    @admin.display(description="حذف")
    def delete_action(self, obj):
        try:
            url = reverse(
                "admin:app_seo_seosetting_delete",
                args=[obj.pk],
            )
            return format_html(
                '<a href="{}" style="color:#dc3545;font-weight:bold;">🗑 حذف</a>',
                url,
            )
        except Exception:
            return "—"

    # =================================================
    #  دکمه «تحلیل مجدد SEO»
    # =================================================

    def response_change(self, request, obj):

        if "_reanalyze_seo" in request.POST:
            try:
                from .analyzer import analyze_and_save

                result = analyze_and_save(obj)

                messages.success(
                    request,
                    f"✅ تحلیل مجدد انجام شد. امتیاز: {result['score']} / 100"
                )
            except Exception as e:
                messages.error(
                    request,
                    f"❌ خطا در تحلیل: {e}"
                )

            return redirect(request.path)

        return super().response_change(request, obj)


# =====================================================
#  SEODefault Admin
# =====================================================

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
                    "می‌توانید از متغیرهای {title} و {site} استفاده کنید."
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
        return obj.title_template[:50] + (
            "…" if len(obj.title_template) > 50 else ""
        )


# =====================================================
#  SEOAnalysisLog Admin
# =====================================================

@admin.register(SEOAnalysisLog)
class SEOAnalysisLogAdmin(admin.ModelAdmin):

    list_display = (
        "seo_setting",
        "score_badge",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "seo_setting__title",
        "seo_setting__page_key",
    )

    readonly_fields = (
        "seo_setting",
        "score",
        "checks",
        "created_at",
    )

    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    @admin.display(description="امتیاز")
    def score_badge(self, obj):
        color = _score_color(obj.score)
        return format_html(
            '<span style="background:{};color:#fff;'
            'padding:2px 8px;border-radius:10px;font-size:11px;">'
            '{} / 100</span>',
            color, obj.score,
        )


# =====================================================
#  عنوان پنل ادمین
# =====================================================

admin.site.site_header = "🚀 پنل مدیریت SEO"
admin.site.site_title = "SEO Admin"
admin.site.index_title = "مدیریت سئو و بهینه‌سازی"