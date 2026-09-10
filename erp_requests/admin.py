
from django.contrib import admin, messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Request


# =========================================================
# درخواست
# =========================================================

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):

    # =====================================================
    # لیست درخواست‌ها
    # =====================================================

    list_display = (
        "number",
        "project_name",
        "priority_display",
        "status_display",
        "created_at",
        "sent_to_execution_at",
        "execution_link",
    )

    # =====================================================
    # فیلترها
    # =====================================================

    list_filter = (
        "status",
        "priority",
        "created_at",
    )

    # =====================================================
    # جستجو
    # =====================================================

    search_fields = (
        "number",
        "project_name",
        "description",
        "requester_note",
    )

    # =====================================================
    # فیلدهای فقط خواندنی
    # =====================================================

    readonly_fields = (
        "number",
        "created_at",
        "sent_to_execution_at",
        "requester_completed_at",
        "completed_at",
        "updated_at",
    )

    # =====================================================
    # فرم
    # =====================================================

    fieldsets = (

        # -------------------------------------------------
        # اطلاعات اصلی
        # -------------------------------------------------

        (
            "اطلاعات درخواست",
            {
                "fields": (
                    "number",
                    "project_name",
                    "description",
                    "priority",
                    "status",
                )
            },
        ),

        # -------------------------------------------------
        # موارد درخواستی
        # -------------------------------------------------

        (
            "موارد درخواستی",
            {
                "fields": (
                    "item_1",
                    "quantity_1",

                    "item_2",
                    "quantity_2",

                    "item_3",
                    "quantity_3",

                    "item_4",
                    "quantity_4",

                    "item_5",
                    "quantity_5",
                )
            },
        ),

        # -------------------------------------------------
        # توضیحات
        # -------------------------------------------------

        (
            "توضیحات درخواست",
            {
                "fields": (
                    "requester_note",
                )
            },
        ),

        # -------------------------------------------------
        # تاریخ‌ها
        # -------------------------------------------------

        (
            "تاریخ و ساعت گردش",
            {
                "fields": (
                    "created_at",
                    "sent_to_execution_at",
                    "requester_completed_at",
                    "completed_at",
                    "updated_at",
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
    # اکشن‌ها
    # =====================================================

    actions = (
        "send_to_execution",
    )

    # =====================================================
    # ارسال درخواست به اجرایات
    # =====================================================

    @admin.action(
        description="ارسال درخواست‌های انتخاب‌شده به اجرایات"
    )
    def send_to_execution(self, request, queryset):

        from erp_execution.models import (
            ExecutionRequest,
            ExecutionItem,
        )

        success_count = 0
        skipped_count = 0

        for obj in queryset:

            # -------------------------------------------------
            # فقط درخواست‌های جدید قابل ارسال هستند
            # -------------------------------------------------

            if obj.status != "NEW":
                skipped_count += 1
                continue

            with transaction.atomic():

                # -------------------------------------------------
                # ساخت یا دریافت درخواست اجرایات
                # -------------------------------------------------

                execution, created = (
                    ExecutionRequest.objects.get_or_create(
                        request=obj,
                        defaults={
                            "request_number": obj.number,
                            "project_name": obj.project_name,
                            "status": "NEW",
                            "requester_description": obj.description,
                        },
                    )
                )

                # -------------------------------------------------
                # انتقال اقلام
                # -------------------------------------------------

                if created:

                    items = [
                        (
                            1,
                            obj.item_1,
                            obj.quantity_1,
                        ),
                        (
                            2,
                            obj.item_2,
                            obj.quantity_2,
                        ),
                        (
                            3,
                            obj.item_3,
                            obj.quantity_3,
                        ),
                        (
                            4,
                            obj.item_4,
                            obj.quantity_4,
                        ),
                        (
                            5,
                            obj.item_5,
                            obj.quantity_5,
                        ),
                    ]

                    for item_number, item_name, quantity in items:

                        # قلم خالی
                        if not item_name:
                            continue

                        # تعداد صفر یا منفی
                        if quantity <= 0:
                            continue

                        ExecutionItem.objects.create(
                            execution=execution,
                            item_number=item_number,
                            item_name=item_name,
                            quantity=quantity,
                            unit="عدد",
                        )

                # -------------------------------------------------
                # تغییر وضعیت درخواست اصلی
                # -------------------------------------------------

                obj.status = "SENT_TO_EXECUTION"
                obj.sent_to_execution_at = timezone.now()

                obj.save(
                    update_fields=[
                        "status",
                        "sent_to_execution_at",
                        "updated_at",
                    ]
                )

                success_count += 1

        # =====================================================
        # پیام نتیجه
        # =====================================================

        if success_count:

            self.message_user(
                request,
                f"{success_count} درخواست با موفقیت به اجرایات ارسال شد.",
                messages.SUCCESS,
            )

        if skipped_count:

            self.message_user(
                request,
                f"{skipped_count} درخواست به دلیل وضعیت فعلی ارسال نشد.",
                messages.WARNING,
            )

    # =====================================================
    # نمایش اولویت
    # =====================================================

    @admin.display(
        description="اولویت",
        ordering="priority",
    )
    def priority_display(self, obj):

        return obj.get_priority_display()

    # =====================================================
    # نمایش وضعیت
    # =====================================================

    @admin.display(
        description="وضعیت",
        ordering="status",
    )
    def status_display(self, obj):

        colors = {
            "NEW": "#2563eb",
            "SENT_TO_EXECUTION": "#7c3aed",
            "IN_EXECUTION": "#d97706",
            "SENT_TO_WAREHOUSE": "#0891b2",
            "IN_WAREHOUSE": "#0e7490",
            "WAITING_REQUESTER": "#ca8a04",
            "COMPLETED_BY_REQUESTER": "#15803d",
            "SENT_TO_FINANCE": "#9333ea",
            "INVOICED": "#16a34a",
            "COMPLETED": "#166534",
            "REJECTED": "#dc2626",
            "CANCELLED": "#6b7280",
        }

        color = colors.get(
            obj.status,
            "#374151",
        )

        return format_html(
            '<strong style="color:{};">{}</strong>',
            color,
            obj.get_status_display(),
        )

    # =====================================================
    # لینک اجرایات
    # =====================================================

    @admin.display(
        description="اجرایات"
    )
    def execution_link(self, obj):

        # هنوز به اجرایات ارسال نشده
        if obj.status == "NEW":
            return "-"

        try:
            # related_name در ExecutionRequest:
            # related_name="execution_request"
            execution = obj.execution_request

        except Exception:
            return "-"

        url = reverse(
            "admin:erp_execution_executionrequest_change",
            args=[execution.pk],
        )

        return format_html(
            '<a href="{}">مشاهده اجرایات</a>',
            url,
        )

