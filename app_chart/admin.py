from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin

from .models import Person, BoardMember


# ---------------------------------------
#   GLOBAL ACTION BUTTONS (EDIT + DELETE)
# ---------------------------------------
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
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);
                    display:inline-flex;
                    align-items:center;
                    gap:5px;
               ">
                ✏️
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
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);
                    display:inline-flex;
                    align-items:center;
                    gap:5px;
               ">
                🗑
            </a>
        </div>
        """,
        edit_url,
        delete_url,
    )


admin_action_buttons.short_description = "عملیات"


class ActionButtonsMixin:
    """Mixin برای اضافه کردن ستون عملیات (ویرایش + حذف) به ادمین"""

    def admin_actions(self, obj):
        return admin_action_buttons(obj)

    admin_actions.short_description = "عملیات"


@admin.register(Person)
class PersonAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):

    actions = None

    list_display = (
        "order",
        "photo_icon",
        "name_icon",
        "position_icon",
        "parent",
        "ceo_icon",
        "admin_actions",
    )

    list_filter = ("parent", "is_ceo")
    search_fields = ("name_fa", "name_en", "position_fa", "position_en")

    ordering = ("order",)
    sortable_by = ("order",)

    readonly_fields = ("image_preview",)

    fieldsets = (
        ("👤 اطلاعات", {
            "fields": ("name_fa", "name_en"),
        }),
        ("💼 سمت", {
            "fields": ("position_fa", "position_en"),
        }),
        ("🖼️ تصویر", {
            "fields": ("photo", "image_preview"),
        }),
        ("🏛️ ساختار سازمانی", {
            "fields": ("parent", "is_ceo"),
        }),
        ("☎️ تماس و توضیحات", {
            "fields": ("content_fa", "content_en", "phone", "email"),
        }),
    )

    # فقط یک مدیرعامل
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        qs = Person.objects.filter(is_ceo=True)
        if obj:
            qs = qs.exclude(pk=obj.pk)

        if qs.exists():
            form.base_fields["is_ceo"].disabled = True
            form.base_fields["is_ceo"].help_text = "فقط یک مدیرعامل مجاز است."

        return form

    def save_model(self, request, obj, form, change):
        if obj.is_ceo:
            qs = Person.objects.filter(is_ceo=True)
            if obj.pk:
                qs = qs.exclude(pk=obj.pk)
            if qs.exists():
                raise ValidationError("فقط یک مدیرعامل می‌تواند وجود داشته باشد.")
        super().save_model(request, obj, form, change)

    # UI
    def photo_icon(self, obj):
        if obj.photo:
            return format_html(
                "<img src='{}' width='42' height='42' style='border-radius:6px;object-fit:cover;'>",
                obj.photo.url
            )
        return "—"
    photo_icon.short_description = "عکس"

    def image_preview(self, obj):
        if obj.photo:
            return format_html(
                "<img src='{}' width='180' style='border-radius:12px;'>",
                obj.photo.url
            )
        return "تصویری ثبت نشده"
    image_preview.short_description = "پیش‌نمایش"

    def name_icon(self, obj):
        return format_html("<strong>{}</strong>", obj.name_fa)
    name_icon.short_description = "نام"

    def position_icon(self, obj):
        return obj.position_fa
    position_icon.short_description = "سمت"

    def ceo_icon(self, obj):
        return "🟢 مدیرعامل" if obj.is_ceo else "—"
    ceo_icon.short_description = "مدیرعامل"


@admin.register(BoardMember)
class BoardMemberAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):

    actions = None

    list_display = (
        "order",
        "photo_icon",
        "name_icon",
        "position_icon",
        "parent",
        "chairman_icon",
        "admin_actions",
    )

    list_filter = ("parent", "is_ceo")
    search_fields = ("name_fa", "name_en", "position_fa", "position_en")

    ordering = ("order",)
    sortable_by = ("order",)

    readonly_fields = ("image_preview",)

    fieldsets = (
        ("👤 اطلاعات", {
            "fields": ("name_fa", "name_en"),
        }),
        ("💼 سمت در هیأت‌مدیره", {
            "fields": ("position_fa", "position_en"),
        }),
        ("🖼️ تصویر", {
            "fields": ("photo", "image_preview"),
        }),
        ("🏛️ ساختار هیأت‌مدیره", {
            "fields": ("parent", "is_ceo"),
        }),
        ("☎️ تماس و توضیحات", {
            "fields": ("content_fa", "content_en", "phone", "email"),
        }),
    )

    # فقط یک رئیس هیأت‌مدیره
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        qs = BoardMember.objects.filter(is_ceo=True)
        if obj:
            qs = qs.exclude(pk=obj.pk)

        if qs.exists():
            form.base_fields["is_ceo"].disabled = True
            form.base_fields["is_ceo"].help_text = "فقط یک رئیس هیأت‌مدیره مجاز است."

        return form

    def save_model(self, request, obj, form, change):
        if obj.is_ceo:
            qs = BoardMember.objects.filter(is_ceo=True)
            if obj.pk:
                qs = qs.exclude(pk=obj.pk)
            if qs.exists():
                raise ValidationError("فقط یک رئیس هیأت‌مدیره می‌تواند وجود داشته باشد.")
        super().save_model(request, obj, form, change)

    # UI
    def photo_icon(self, obj):
        if obj.photo:
            return format_html(
                "<img src='{}' width='42' height='42' style='border-radius:6px;object-fit:cover;'>",
                obj.photo.url
            )
        return "—"
    photo_icon.short_description = "عکس"

    def image_preview(self, obj):
        if obj.photo:
            return format_html(
                "<img src='{}' width='180' style='border-radius:12px;'>",
                obj.photo.url
            )
        return "تصویری ثبت نشده"
    image_preview.short_description = "پیش‌نمایش"

    def name_icon(self, obj):
        return format_html("<strong>{}</strong>", obj.name_fa)
    name_icon.short_description = "نام"

    def position_icon(self, obj):
        return obj.position_fa
    position_icon.short_description = "سمت"

    def chairman_icon(self, obj):
        return "🟢 رئیس هیأت‌مدیره" if obj.is_ceo else "—"
    chairman_icon.short_description = "رئیس"