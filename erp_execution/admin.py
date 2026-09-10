
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    ExecutionRequest,
    ExecutionItem,
)


# =========================================================
# اقلام اجرایات
# =========================================================

class ExecutionItemInline(admin.TabularInline):

    model = ExecutionItem

    extra = 1

    fields = (
        "item_number",
        "item_name",
        "quantity",
        "unit",
        "description",
    )

    ordering = (
        "item_number",
    )


# =========================================================
# درخواست اجرایات
# =========================================================

@admin.register(ExecutionRequest)
class ExecutionRequestAdmin(admin.ModelAdmin):

    # =====================================================
    # لیست
    # =====================================================

    list_display = (
        "request_number",
        "project_name",
        "executor",
        "status_display",
        "created_at",
        "seen_at",
        "started_at",
        "completed_at",
    )

    # =====================================================
    # فیلترها
    # =====================================================

    list_filter = (
        "status",
        "created_at",
        "seen_at",
        "started_at",
        "completed_at",
    )

    # =====================================================
    # جستجو
    # =====================================================

    search_fields = (
        "request_number",
        "project_name",
        "description",
        "requester_description",
        "execution_description",
        "executor__username",
        "executor__first_name",
        "executor__last_name",
        "request__number",
    )

    # =====================================================
    # فیلدهای User
    # =====================================================

    raw_id_fields = (
        "executor",
    )

    # =====================================================
    # اتصال به درخواست اصلی
    # =====================================================

    autocomplete_fields = (
        "request",
    )

    # =====================================================
    # اقلام
    # =====================================================

    inlines = (
        ExecutionItemInline,
    )

    # =====================================================
    # فیلدهای فقط خواندنی
    # =====================================================

    readonly_fields = (
        "request_number",
        "project_name",
        "description",
        "requester_description",
        "created_at",
        "seen_at",
        "started_at",
        "completed_at",
    )

    # =====================================================
    # فرم
    # =====================================================

    fieldsets = (

        # -------------------------------------------------
        # درخواست اصلی
        # -------------------------------------------------

        (
            "درخواست اصلی",
            {
                "fields": (
                    "request",
                    "request_number",
                    "project_name",
                )
            },
        ),

        # -------------------------------------------------
        # مسئول اجرایات
        # -------------------------------------------------

        (
            "مسئول اجرایات",
            {
                "fields": (
                    "executor",
                    "status",
                )
            },
        ),

        # -------------------------------------------------
        # شرح درخواست
        # -------------------------------------------------

        (
            "شرح درخواست",
            {
                "fields": (
                    "description",
                    "requester_description",
                )
            },
        ),

        # -------------------------------------------------
        # گزارش اجرایات
        # -------------------------------------------------

        (
            "گزارش اجرایات",
            {
                "fields": (
                    "execution_description",
                )
            },
        ),

        # -------------------------------------------------
        # زمان‌بندی
        # -------------------------------------------------

        (
            "زمان‌بندی گردش درخواست",
            {
                "fields": (
                    "created_at",
                    "seen_at",
                    "started_at",
                    "completed_at",
                )
            },
        ),
    )

    # =====================================================
    # ترتیب
    # =====================================================

    ordering = (
        "-created_at",
    )

    # =====================================================
    # وضعیت رنگی
    # =====================================================

    @admin.display(
        description="وضعیت",
        ordering="status",
    )
    def status_display(self, obj):

        colors = {
            "NEW": "#2563eb",
            "SEEN": "#7c3aed",
            "IN_PROGRESS": "#d97706",
            "WAITING_WAREHOUSE": "#0891b2",
            "COMPLETED": "#16a34a",
            "REJECTED": "#dc2626",
        }

        return format_html(
            '<strong style="color:{};">{}</strong>',
            colors.get(
                obj.status,
                "#374151",
            ),
            obj.get_status_display(),
        )

