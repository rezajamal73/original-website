from django.contrib import admin
from django.utils.html import format_html
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


def admin_delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        """
        <a href="{}"
           style="
                background:#d7263d;
                color:white;
                padding:6px 10px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
           ">
           🗑 حذف
        </a>
        """,
        url,
    )

admin_delete_button.short_description = "حذف"


def make_status_icon(published_label: str, draft_label: str):
    """Factory تولید status_icon برای جلوگیری از تکرار کد"""
    def status_icon(self, obj):
        if obj.status == "published":
            return format_html("<b style='color:green;'>{}</b>", published_label)
        return format_html("<b style='color:red;'>{}</b>", draft_label)
    status_icon.short_description = "وضعیت"
    return status_icon


@admin.register(HeroSliderSetting)
class HeroSliderSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HeroSliderSetting.objects.exists()


@admin.register(HeroBanner)
class HeroBannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "display_title",
        "status_icon",
        "admin_delete",
    )

    search_fields = (
        "label_fa",
        "label_en",
        "title_p1_fa",
        "title_p1_en",
    )

    list_filter = ("status",)
    readonly_fields = ("image_preview",)

    fieldsets = (
        ("📌 وضعیت انتشار", {"fields": ("status",)}),
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
        ("🖼️ تصویر بنر", {"fields": ("image", "image_preview")}),
    )

    def display_title(self, obj):
        return obj.label_fa or obj.title_p1_fa or "— بدون عنوان —"
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

    def admin_delete(self, obj):
        return admin_delete_button(obj)
    admin_delete.short_description = "حذف"


@admin.register(OtherBanner)
class OtherBannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "display_title",
        "status_icon",
        "admin_delete",
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

    def admin_delete(self, obj):
        return admin_delete_button(obj)
    admin_delete.short_description = "حذف"


@admin.register(SpecialProductBanner)
class SpecialProductBannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "display_title",
        "status_icon",
        "admin_delete",
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

    def admin_delete(self, obj):
        return admin_delete_button(obj)
    admin_delete.short_description = "حذف"


@admin.register(MainBanner)
class MainBannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    actions = None

    list_display = (
        "order",
        "image_icon",
        "title_fa",
        "status_icon",
        "admin_delete",
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

    def admin_delete(self, obj):
        return admin_delete_button(obj)
    admin_delete.short_description = "حذف"

    @admin.register(AboutBanner)
    class AboutBannerAdmin(admin.ModelAdmin):
        actions = None

        list_display = (
            "image1_icon",
            "image2_icon",
            "status",
            "admin_delete",
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

        def admin_delete(self, obj):
            return admin_delete_button(obj)

        admin_delete.short_description = "حذف"