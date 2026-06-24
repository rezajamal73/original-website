from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin
from app_blog.models import blog, blog_Category, blog_Tag, BlogImage
from django.utils.safestring import mark_safe


# ---------------------------------------
#   GLOBAL DELETE BUTTON
# ---------------------------------------
def admin_delete_button(obj):
    url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=[obj.pk])
    return format_html(
        '''
        <a href="{}"
           style="
                background:#d7263d;
                color:white;
                padding:6px 10px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
                display:inline-flex;
                align-items:center;
                gap:5px;
                box-shadow:0 2px 5px rgba(0,0,0,0.2);
           ">
            🗑
        </a>
        ''',
        url
    )


admin_delete_button.short_description = ""


# ---------------------------------------
#   INLINE: BLOG IMAGE
# ---------------------------------------
class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    fields = ("show_image", "image", "order")
    readonly_fields = ("show_image",)

    def show_image(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='80' style='border-radius:8px; box-shadow:0 0 6px #aaa;'>",
                obj.image.url
            )
        return "—"

    show_image.short_description = "پیش‌نمایش"


# ---------------------------------------
#   CATEGORY ADMIN (Sortable)
# ---------------------------------------
@admin.register(blog_Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("created_at_fa", "slug")
    ordering = ("order",)

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)


# ---------------------------------------
#   TAG ADMIN (Sortable)
# ---------------------------------------
@admin.register(blog_Tag)
class TagAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("created_at_fa", "slug")
    ordering = ("order",)

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)


# ---------------------------------------
#   BLOG ADMIN
# ---------------------------------------
@admin.register(blog)
class BlogAdmin( admin.ModelAdmin):
    # SortableAdminMixin,
    list_display = (
        # "order",
        "image_icon",
        "title_icon",
        "status_icon",
        "category_icon",
        "tag_icon",
        "date_icon",
        "delete_button",
    )

    list_filter = ("status", "category")
    search_fields = ("title_fa", "title_en")

    readonly_fields = ("show_image_in_field", "slug")

    inlines = [BlogImageInline]

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("status", "author"),
            "classes": ("collapse",),
        }),
        ("🖼️ تصویر", {
            "fields": ("image", "show_image_in_field",),
        }),
        ("📄 فارسی", {
            "fields": ("title_fa", "content_1_fa", "content_2_fa"),
        }),
        ("📄 انگلیسی", {
            "fields": ("title_en", "content_1_en", "content_2_en", "slug",),
        }),
        ("📂️ دسته بندی", {
            "fields": ("category", "tags"),
        }),
        ("📎 پیوست", {
            "fields": ("upload_file",),
        }),
        ("🗓️ تاریخ‌ ها", {
            "fields": ("publish_date_fa", "publish_date_en"),
        }),
    )



    # IMAGE ICON – list view
    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.image.url
            )
        return "🖼️"

    image_icon.short_description = "پوستر"

    # IMAGE PREVIEW – form view

    def show_image_in_field(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='180' style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.image.url
            )
        return "تصویری آپلود نشده است"

    show_image_in_field.short_description = "پیش نمایش"

    # TITLE
    def title_icon(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    # STATUS
    def status_icon(self, obj):
        if obj.status == "published":
            return mark_safe("<b style='color:green'>منتشر شده</b>")
        return mark_safe("<b style='color:red'>پیش‌نویس</b>")

    status_icon.short_description = "وضعیت"

    # CATEGORY
    def category_icon(self, obj):
        return obj.category.title_fa if obj.category else "—"

    category_icon.short_description = "دسته بندی"

    # TAGS (NEW) – ICON
    def tag_icon(self, obj):
        tags = obj.tags.all()

        if not tags.exists():
            return "—"

        html = "<div style='display:flex; flex-wrap:wrap; gap:6px;'>"

        for t in tags:
            html += (
                f"<span style='background:#E8F0FE; color:#1A73E8; "
                f"padding:3px 8px; border-radius:6px; font-size:12px;'>"
                f"🏷️ {t.title_fa}</span>"
            )

        html += "</div>"

        return mark_safe(html)

    tag_icon.short_description = "برچسب‌ها"

    # DATE
    def date_icon(self, obj):
        return obj.publish_date_fa

    date_icon.short_description = "تاریخ انتشار(شمسی)"

    # DELETE BUTTON
    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"
