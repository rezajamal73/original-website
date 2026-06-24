from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import (
    CorporateSection,
    CorporateText,
    CorporateImage,
    CorporateAttachment,
    CorporateStatistic,
    AboutYear,
    AboutItem,
    GroupCompany,
    SiteMainInfo,
    FollowUsLink,
    DepartmentContact
)


# =====================================================
# دکمه حذف عمومی
# =====================================================
def admin_delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk]
    )
    return format_html(
        "<a href='{}' style='background:#d7263d;color:#fff;"
        "padding:6px 10px;border-radius:8px;text-decoration:none;"
        "font-weight:bold'>🗑 حذف</a>",
        url
    )


# =====================================================
# INLINE: سال تأسیس (فقط یک مورد)
# =====================================================
class AboutYearInline(admin.StackedInline):
    model = AboutYear
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name_plural = "📅 سابقه تأسیس"

    def has_add_permission(self, request, obj=None):
        if obj and hasattr(obj, "about_year"):
            return False
        return super().has_add_permission(request, obj)


# =====================================================
# INLINE: آیتم‌های درباره ما (حداکثر ۱۵)
# =====================================================
class AboutItemInline(SortableAdminMixin, admin.StackedInline):
    model = AboutItem
    extra = 0
    ordering = ("display_order",)
    verbose_name_plural = "🧾 آیتم‌های درباره ما"

    def has_add_permission(self, request, obj=None):
        if obj and obj.about_items.count() >= 15:
            return False
        return super().has_add_permission(request, obj)


# =====================================================
# INLINE: بلاک‌های متنی
# =====================================================
class CorporateTextInline(SortableAdminMixin, admin.StackedInline):
    model = CorporateText
    extra = 1
    ordering = ("display_order",)
    show_change_link = True
    verbose_name_plural = "🧩 بلاک‌های متنی"


# =====================================================
# INLINE: تصاویر
# =====================================================
class CorporateImageInline(SortableAdminMixin, admin.TabularInline):
    model = CorporateImage
    extra = 1
    fields = ("preview", "image", "display_order")
    readonly_fields = ("preview",)
    ordering = ("display_order",)
    verbose_name_plural = "🖼 تصاویر"

    def preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='80' style='border-radius:6px;'>",
                obj.image.url
            )
        return "—"

    preview.short_description = "پیش‌نمایش تصویر"


# =====================================================
# INLINE: پیوست‌ها
# =====================================================
class CorporateAttachmentInline(SortableAdminMixin, admin.TabularInline):
    model = CorporateAttachment
    extra = 1
    fields = ("display_order", "title", "file")
    ordering = ("display_order",)
    verbose_name_plural = "📎 فایل‌های پیوست"


# =====================================================
# CORPORATE SECTION ADMIN
# =====================================================
@admin.register(CorporateSection)
class CorporateSectionAdmin(admin.ModelAdmin):
    list_display = (
        "section_title",
        "publish_status",
        "created_at",
        "delete_action",
    )

    list_filter = ("section_type", "is_published")
    ordering = ("section_type",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("📌 اطلاعات اصلی", {
            "fields": ("section_type", "is_published"),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj and obj.section_type == "about":
            return (AboutYearInline, AboutItemInline, CorporateTextInline)
        return (CorporateTextInline,)

    def section_title(self, obj):
        return format_html("🏢 <b>{}</b>", obj.get_section_type_display())

    section_title.short_description = "عنوان بخش"

    def publish_status(self, obj):
        return format_html(
            "<b style='color:{}'>{}</b>",
            "green" if obj.is_published else "red",
            "منتشر شده" if obj.is_published else "غیرفعال",
        )

    publish_status.short_description = "وضعیت انتشار"

    def delete_action(self, obj):
        return admin_delete_button(obj)

    delete_action.short_description = "حذف"


# =====================================================
# CORPORATE TEXT ADMIN
# =====================================================
@admin.register(CorporateText)
class CorporateTextAdmin(admin.ModelAdmin):
    list_display = (
        "text_title",
        "section",
        "display_order",
        "delete_action",
    )

    list_filter = ("section",)
    ordering = ("section", "display_order")

    fieldsets = (
        ("📌 تنظیمات", {
            "fields": ("section", "display_order"),
        }),
        ("📄 محتوای فارسی", {
            "fields": ("title_fa", "content_fa"),
        }),
        ("🌐 محتوای انگلیسی", {
            "fields": ("title_en", "content_en"),
        }),
    )

    inlines = (CorporateImageInline, CorporateAttachmentInline)

    def text_title(self, obj):
        return obj.title_fa or obj.title_en or "—"

    text_title.short_description = "عنوان بلاک"

    def delete_action(self, obj):
        return admin_delete_button(obj)

    delete_action.short_description = "حذف"


# =====================================================
# CORPORATE STATISTIC ADMIN
# =====================================================
@admin.register(CorporateStatistic)
class CorporateStatisticAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_order",
        "icon_preview",
        "title_fa",
        "title_en",
        "value_preview",
        "is_active",
        "delete_action",
    )

    list_editable = ("is_active",)
    ordering = ("display_order",)
    readonly_fields = ("icon_preview", "created_at")
    actions = None

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("is_active", "display_order"),
        }),
        ("📊 اطلاعات آماری", {
            "fields": ("title_fa",  "title_en", "value", "suffix"),
        }),
        ("🎨 آیکن", {
            "fields": ("icon_svg", "icon_preview"),
        }),
    )

    def has_add_permission(self, request):
        return CorporateStatistic.objects.count() < 4

    def icon_preview(self, obj):
        if obj.icon_svg:
            return format_html(
                "<img src='{}' width='40' style='background:#f5f5f5;"
                "padding:6px;border-radius:10px;'>",
                obj.icon_svg.url
            )
        return "—"

    icon_preview.short_description = "پیش‌نمایش آیکن"

    def value_preview(self, obj):
        return format_html("<b>{} {}</b>", obj.value, obj.suffix or "")

    value_preview.short_description = "مقدار"

    def delete_action(self, obj):
        return admin_delete_button(obj)

    delete_action.short_description = "حذف"


# =====================================================
# GROUP COMPANY ADMIN
# =====================================================
@admin.register(GroupCompany)
class GroupCompanyAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_order",
        "logo_preview",
        "name",
        "website_link",
        "is_active",
        "delete_action",
    )

    list_editable = ("is_active",)
    ordering = ("display_order",)
    list_filter = ("is_active",)
    readonly_fields = ("logo_preview", "created_at")
    actions = None

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("is_active",),
        }),
        ("🏢 اطلاعات شرکت", {
            "fields": ("name", "logo", "logo_preview", "website"),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                "<img src='{}' width='80' "
                "style='border-radius:12px;background:#f5f5f5;padding:6px;'>",
                obj.logo.url
            )
        return "—"

    logo_preview.short_description = "لوگو"

    def website_link(self, obj):
        if obj.website:
            return format_html(
                "<a href='{}' target='_blank' rel='noopener' "
                "style='color:#0d6efd;font-weight:bold'>🌐 مشاهده سایت</a>",
                obj.website
            )
        return "—"

    website_link.short_description = "وب‌سایت"

    def delete_action(self, obj):
        return admin_delete_button(obj)

    delete_action.short_description = "حذف"


# =====================================================
# SITE MAIN INFO ADMIN
# =====================================================
@admin.register(SiteMainInfo)
class SiteMainInfoAdmin(admin.ModelAdmin):
    actions = None
    readonly_fields = (
        "header_logo_preview",
        "footer_logo_preview",
        "sidebar_logo_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("🏢 مشخصات اصلی شرکت", {
            "fields": (
                "designer_name_fa",
                "designer_name_en",
                "name_company_p1_fa",
                "name_company_p2_fa",
                "name_company_p1_en",
                "name_company_p2_en",
                "slogan_fa",
                "slogan_en",
            ),
        }),

        ("🎨 لوگوها", {
            "fields": (
                "header_logo",
                "header_logo_preview",
                "footer_logo",
                "footer_logo_preview",
                "sidebar_logo",
                "sidebar_logo_preview",
            ),
        }),

        ("📞 اطلاعات تماس", {
            "fields": (
                "phone_1",
                "phone_2",
                "phone_3",
                "phone_4",
                "phone_5",
                "suport_phone",
            ),
        }),

        ("📠 فکس، ایمیل و کد پستی", {
            "fields": (
                "fax_1",
                "fax_2",
                "fax_3",
                "email",
                "postal_code",
            ),
        }),

        ("📍 آدرس شرکت", {
            "fields": (
                "address_fa",
                "address_en",
            ),
        }),
        ("🛡️ تماس حراست", {
            "fields": (
                "phone_security_1",
                "phone_security_2",
                "phone_security_3",
                "email_security",
                "fax_security",
            ),
        }),

        ("🗓️ زمان و روزهای فعالیت", {
            "fields": (
                "work_days_fa",
                "work_days_en",
            ),
        }),

        ("⏱️ اطلاعات سیستمی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
        }),
    )

    def has_add_permission(self, request):
        return not SiteMainInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def header_logo_preview(self, obj):
        if obj.header_logo:
            return format_html(
                "<img src='{}' width='120' style='background:#f5f5f5;"
                "padding:8px;border-radius:10px;'>",
                obj.header_logo.url
            )
        return "—"

    header_logo_preview.short_description = "پیش‌نمایش لوگوی هدر"

    def footer_logo_preview(self, obj):
        if obj.footer_logo:
            return format_html(
                "<img src='{}' width='120' style='background:#f5f5f5;"
                "padding:8px;border-radius:10px;'>",
                obj.footer_logo.url
            )
        return "—"

    footer_logo_preview.short_description = "پیش‌نمایش لوگوی فوتر"

    def sidebar_logo_preview(self, obj):
        if obj.sidebar_logo:
            return format_html(
                "<img src='{}' width='120' style='background:#f5f5f5;"
                "padding:8px;border-radius:10px;'>",
                obj.sidebar_logo.url
            )
        return "—"

    sidebar_logo_preview.short_description = "پیش‌نمایش لوگوی سایدبار"


# =====================================================
# FOLLOW US LINK ADMIN (مستقل)
# =====================================================
@admin.register(FollowUsLink)
class FollowUsLinkAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت لینک‌های «ما را دنبال کنید»
    """

    list_display = (
        "display_order",
        "icon_preview",
        "title",
        "is_active",
        "delete_action",
    )

    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "url")
    ordering = ("display_order",)
    actions = None

    readonly_fields = ("icon_preview",)

    fieldsets = (
        ("📌 وضعیت انتشار", {
            "fields": ("is_active", "display_order"),
        }),
        ("🌐 اطلاعات لینک شبکه اجتماعی", {
            "fields": ("title", "url"),
        }),
        ("🎨 آیکن شبکه اجتماعی", {
            "fields": ("svg_icon", "icon_preview"),
        }),
    )

    def icon_preview(self, obj):
        """
        پیش‌نمایش آیکن SVG
        فایل SVG به‌صورت امن و بدون اجرای کد نمایش داده می‌شود
        """
        if obj.svg_icon:
            return format_html(
                "<img src='{}' width='36' height='36' "
                "style='background:#f5f5f5;"
                "padding:6px;border-radius:8px;' />",
                obj.svg_icon.url
            )
        return "—"

    icon_preview.short_description = "پیش‌نمایش آیکن"

    def delete_action(self, obj):
        return admin_delete_button(obj)

    delete_action.short_description = "حذف"



@admin.register(DepartmentContact)
class DepartmentContactAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_order",
        "department_fa",
        "department_en",
        "phone_main",
        "phone_alt",
        "delete_action",
    )

    # ✅ لینک ویرایش (حل خطای E124)
    list_display_links = (
        "department_fa",
    )

    # ✅ قابل ویرایش در لیست
    list_editable = (
        "display_order",
    )

    search_fields = (
        "department_name_fa",
        "department_name_en",
        "phone_1",
        "phone_2",
    )
    ordering = ("display_order",)
    actions = None

    fieldsets = (
        ("🏢 اطلاعات دپارتمان", {
            "fields": (
                "department_name_fa",
                "department_name_en",
            )
        }),
        ("📞 شماره‌های تماس", {
            "fields": (
                "phone_1",
                "phone_2",
                "email",
            )
        }),
        ("🔢 تنظیمات نمایش", {
            "fields": (
                "display_order",
            )
        }),
    )

    # -------- نمایش‌های سفارشی --------
    def department_fa(self, obj):
        return format_html("<b>{}</b>", obj.department_name_fa)
    department_fa.short_description = "دپارتمان (FA)"

    def department_en(self, obj):
        return obj.department_name_en
    department_en.short_description = "Department (EN)"

    def phone_main(self, obj):
        return format_html(
            "<a href='tel:{}' style='font-weight:bold'>{}</a>",
            obj.phone_1,
            obj.phone_1
        )
    phone_main.short_description = "تماس اصلی"

    def phone_alt(self, obj):
        if obj.phone_2:
            return format_html(
                "<a href='tel:{}'>{}</a>",
                obj.phone_2,
                obj.phone_2
            )
        return "—"
    phone_alt.short_description = "تماس جایگزین"

    def delete_action(self, obj):
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
            args=[obj.pk]
        )
        return format_html(
            "<a href='{}' style='background:#d7263d;color:#fff;"
            "padding:6px 10px;border-radius:8px;text-decoration:none;"
            "font-weight:bold'>🗑 حذف</a>",
            url
        )
    delete_action.short_description = "حذف"