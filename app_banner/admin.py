from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from app_banner.models import (
    HeroBanner,
    OtherBanner,
    SpecialProductBanner,
    MainBanner,
    HeroSliderSetting,
    AboutBanner,
)


def admin_action_buttons(obj):
    edit_url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.pk],
    )
    delete_url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        """
        <div style="display:inline-flex; gap:6px; align-items:center;">
            <a href="{}"
               style="
                    background:#1e88e5;
                    color:white;
                    padding:6px 10px;
                    border-radius:8px;
                    text-decoration:none;
                    font-weight:bold;
                    white-space:nowrap;
               ">
               ✏️ ویرایش
            </a>
            <a href="{}"
               style="
                    background:#d7263d;
                    color:white;
                    padding:6px 10px;
                    border-radius:8px;
                    text-decoration:none;
                    font-weight:bold;
                    white-space:nowrap;
               ">
               🗑 حذف
            </a>
        </div>
        """,
        edit_url,
        delete_url,
    )


admin_action_buttons.short_description = "عملیات"


def make_status_icon(published_label: str, draft_label: str):
    """Factory تولید status_icon برای جلوگیری از تکرار کد"""

    def status_icon(self, obj):
        if obj.status == "published":
            return format_html("<b style='color:green;'>{}</b>", published_label)
        return format_html("<b style='color:red;'>{}</b>", draft_label)

    status_icon.short_description = "وضعیت"
    return status_icon


class ActionButtonsMixin:
    """Mixin برای اضافه کردن ستون عملیات (ویرایش + حذف) به ادمین"""

    def admin_actions(self, obj):
        return admin_action_buttons(obj)

    admin_actions.short_description = "عملیات"


@admin.register(HeroSliderSetting)
class HeroSliderSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HeroSliderSetting.objects.exists()


@admin.register(HeroBanner)
class HeroBannerAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "media_icon",
        "display_title",
        "media_type_display",
        "duration",
        "status_icon",
        "admin_actions",
    )

    search_fields = (
        "label_fa",
        "label_en",
        "title_p1_fa",
        "title_p1_en",
    )

    list_filter = ("status", "media_type")
    readonly_fields = ("media_preview",)

    fieldsets = (
        ("📌 وضعیت انتشار", {"fields": ("status", "order")}),
        ("⏱️ تنظیمات نمایش", {
            "fields": ("duration",),
            "description": "مدت زمان نمایش این اسلاید به ثانیه"
        }),
        ("🎯 نوع مدیا (فقط یکی را انتخاب کنید)", {
            "fields": ("media_type",),
            "description": "⚠️ توجه: پس از انتخاب نوع مدیا، فقط فیلد مربوط به آن را پر کنید. فیلد دیگر باید خالی بماند."
        }),
        ("🖼️ تصویر بنر", {
            "fields": ("image",),
            "description": "فقط در صورتی که «تصویر» را انتخاب کرده‌اید، این فیلد را پر کنید."
        }),
        ("🎬 ویدیو/GIF بنر", {
            "fields": ("video",),
            "description": "فقط در صورتی که «ویدیو / GIF» را انتخاب کرده‌اید، این فیلد را پر کنید. فرمت‌های مجاز: MP4, WebM, OGG, GIF"
        }),
        ("📝 اطلاعات فارسی", {
            "fields": (
                "label_fa",
                "title_p1_fa",
                "title_p2_fa",
                "title_p3_fa",
                "subtitle_fa",
            )
        }),
        ("📝 اطلاعات انگلیسی", {
            "fields": (
                "label_en",
                "title_p1_en",
                "title_p2_en",
                "title_p3_en",
                "subtitle_en",
            )
        }),
        ("👁️ پیش‌نمایش", {"fields": ("media_preview",)}),
    )

    def display_title(self, obj):
        return obj.label_fa or obj.title_p1_fa or "— بدون عنوان —"

    display_title.short_description = "عنوان"

    def media_type_display(self, obj):
        """نمایش نوع مدیا در لیست ادمین"""
        if obj.media_type == "image":
            return mark_safe(
                "<span style='color:#1e88e5; font-weight:bold;'>🖼️ تصویر</span>"
            )
        elif obj.media_type == "video":
            return mark_safe(
                "<span style='color:#d7263d; font-weight:bold;'>🎬 ویدیو</span>"
            )
        return mark_safe(
            "<span style='color:#999;'>—</span>"
        )

    media_type_display.short_description = "نوع مدیا"

    def media_icon(self, obj):
        """آیکون مدیا در لیست ادمین"""
        if obj.media_type == "video" and obj.video:
            ext = obj.video.name.split('.')[-1].lower()
            if ext == 'gif':
                return format_html(
                    "<img src='{}' width='50' style='border-radius:6px;' title='GIF'>",
                    obj.video.url,
                )
            # ✅ اصلاح: mark_safe به جای format_html بدون آرگومان
            return mark_safe(
                "<span style='font-size:24px;' title='ویدیو'>🎬</span>"
            )
        if obj.media_type == "image" and obj.image:
            return format_html(
                "<img src='{}' width='40' style='border-radius:6px;'>",
                obj.image.url,
            )
        return "—"

    media_icon.short_description = "مدیا"

    def media_preview(self, obj):
        """پیش‌نمایش کامل مدیا بر اساس نوع انتخاب‌شده"""
        if obj.media_type == "video" and obj.video:
            ext = obj.video.name.split('.')[-1].lower()
            if ext == 'gif':
                return format_html(
                    "<div style='text-align:center;'>"
                    "<img src='{}' style='max-width:400px; border-radius:10px;'><br>"
                    "<small style='color:#666;'>📁 {}</small>"
                    "</div>",
                    obj.video.url,
                    obj.video.name,
                )
            elif ext in ['mp4', 'webm', 'ogg']:
                return format_html(
                    "<div style='text-align:center;'>"
                    "<video width='400' controls autoplay muted loop style='border-radius:10px;'>"
                    "<source src='{}' type='video/{}'>"
                    "مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند."
                    "</video><br>"
                    "<small style='color:#666;'>📁 {}</small>"
                    "</div>",
                    obj.video.url,
                    ext,
                    obj.video.name,
                )
        if obj.media_type == "image" and obj.image:
            return format_html(
                "<div style='text-align:center;'>"
                "<img src='{}' width='300' style='border-radius:10px;'><br>"
                "<small style='color:#666;'>📁 {}</small>"
                "</div>",
                obj.image.url,
                obj.image.name,
            )
        return mark_safe(
            "<span style='color:#d7263d;'>هیچ مدیایی آپلود نشده است</span>"
        )

    media_preview.short_description = "پیش‌نمایش مدیا"

    status_icon = make_status_icon("✅ منتشر شده", "⛔ پیش‌نویس")


@admin.register(OtherBanner)
class OtherBannerAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "display_title",
        "status_icon",
        "admin_actions",
    )

    search_fields = ("label_fa",)
    list_filter = ("status",)
    readonly_fields = ("image_preview",)

    fieldsets = (
        ("📌 وضعیت انتشار", {"fields": ("status",)}),
        ("🖼️ تصویر بنر", {"fields": ("image", "image_preview")}),
    )

    def has_add_permission(self, request):
        return not OtherBanner.objects.exists()

    def display_title(self, obj):
        return obj.label_fa or "— بدون عنوان —"

    display_title.short_description = "عنوان"

    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='40' style='border-radius:6px;'>",
                obj.image.url,
            )
        return "—"

    image_icon.short_description = "تصویر"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='220' style='border-radius:10px;'>",
                obj.image.url,
            )
        return "تصویری وجود ندارد"

    image_preview.short_description = "پیش‌نمایش تصویر"

    status_icon = make_status_icon("✅ منتشر شده", "⛔ پیش‌نویس")


@admin.register(SpecialProductBanner)
class SpecialProductBannerAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "display_title",
        "status_icon",
        "admin_actions",
    )

    readonly_fields = ("image_preview",)

    fieldsets = (
        ("📌 وضعیت بنر", {"fields": ("status",)}),
        ("🖼️ تصویر بنر", {"fields": ("image", "image_preview")}),
    )

    def has_add_permission(self, request):
        return not SpecialProductBanner.objects.exists()

    def display_title(self, obj):
        return obj.title_fa or "— بنر محصول ویژه —"

    display_title.short_description = "عنوان"

    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='40' style='border-radius:6px;'>",
                obj.image.url,
            )
        return "—"

    image_icon.short_description = "تصویر"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='220' style='border-radius:10px;'>",
                obj.image.url,
            )
        return "تصویری وجود ندارد"

    image_preview.short_description = "پیش‌نمایش تصویر"

    status_icon = make_status_icon("✅ فعال", "⛔ غیرفعال")


@admin.register(MainBanner)
class MainBannerAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "title_fa",
        "status_icon",
        "admin_actions",
    )

    readonly_fields = ("image_preview",)

    fieldsets = (
        ("📌 وضعیت انتشار", {"fields": ("status",)}),
        ("📝 محتوای فارسی", {
            "fields": ("title_p1_fa", "title_p2_fa", "subtitle_fa")
        }),
        ("📝 محتوای انگلیسی", {
            "fields": ("title_p1_en", "title_p2_en", "subtitle_en")
        }),
        ("🖼️ تصویر بنر", {"fields": ("image", "image_preview")}),
    )

    def has_add_permission(self, request):
        return not MainBanner.objects.exists()

    def title_fa(self, obj):
        if obj.title_p1_fa or obj.title_p2_fa:
            return f"{obj.title_p1_fa or ''} | {obj.title_p2_fa or ''}"
        return "— بدون عنوان —"

    title_fa.short_description = "عنوان فارسی"

    def title_en(self, obj):
        if obj.title_p1_en or obj.title_p2_en:
            return f"{obj.title_p1_en or ''} | {obj.title_p2_en or ''}"
        return "—"

    title_en.short_description = "عنوان انگلیسی"

    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='40' style='border-radius:6px;'>",
                obj.image.url,
            )
        return "—"

    image_icon.short_description = "تصویر"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='220' style='border-radius:10px;'>",
                obj.image.url,
            )
        return "تصویری وجود ندارد"

    image_preview.short_description = "پیش‌نمایش تصویر"

    status_icon = make_status_icon("✅ منتشر شده", "⛔ پیش‌نویس")


@admin.register(AboutBanner)
class AboutBannerAdmin(ActionButtonsMixin, admin.ModelAdmin):
    actions = None

    list_display = (
        "image1_icon",
        "image2_icon",
        "status",
        "admin_actions",
    )

    readonly_fields = (
        "image1_preview",
        "image2_preview",
    )

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("status",),
        }),
        ("🖼️ تصویر اول", {
            "fields": ("image_1", "image1_preview"),
        }),
        ("🖼️ تصویر دوم", {
            "fields": ("image_2", "image2_preview"),
        }),
    )

    def has_add_permission(self, request):
        return not AboutBanner.objects.exists()

    def image1_icon(self, obj):
        if obj.image_1:
            return format_html(
                "<img src='{}' width='50' style='border-radius:6px;'>",
                obj.image_1.url,
            )
        return "—"

    image1_icon.short_description = "تصویر اول"

    def image2_icon(self, obj):
        if obj.image_2:
            return format_html(
                "<img src='{}' width='50' style='border-radius:6px;'>",
                obj.image_2.url,
            )
        return "—"

    image2_icon.short_description = "تصویر دوم"

    def image1_preview(self, obj):
        if obj.image_1:
            return format_html(
                "<img src='{}' width='250' style='border-radius:10px;'>",
                obj.image_1.url,
            )
        return "تصویری وجود ندارد"

    image1_preview.short_description = "پیش‌نمایش تصویر اول"

    def image2_preview(self, obj):
        if obj.image_2:
            return format_html(
                "<img src='{}' width='250' style='border-radius:10px;'>",
                obj.image_2.url,
            )
        return "تصویری وجود ندارد"

    image2_preview.short_description = "پیش‌نمایش تصویر دوم"