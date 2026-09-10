
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Warehouse,
    Product,
    Stock,
    WarehouseRequest,
    WarehouseRequestItem,
    StockTransaction,
)


# =========================================================
# انبار
# =========================================================

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "manager",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "manager__username",
        "manager__first_name",
        "manager__last_name",
    )

    # User autocomplete نداریم
    raw_id_fields = (
        "manager",
    )

    list_editable = (
        "is_active",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            "اطلاعات انبار",
            {
                "fields": (
                    "code",
                    "name",
                    "manager",
                    "is_active",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    ordering = (
        "name",
    )


# =========================================================
# کالا
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "unit",
        "minimum_stock",
        "is_active",
        "created_at",
    )

    list_filter = (
        "unit",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    list_editable = (
        "is_active",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            "اطلاعات کالا",
            {
                "fields": (
                    "code",
                    "name",
                    "unit",
                    "minimum_stock",
                    "is_active",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    ordering = (
        "name",
    )


# =========================================================
# موجودی انبار
# =========================================================

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    list_display = (
        "warehouse",
        "product",
        "quantity",
        "stock_status",
        "updated_at",
    )

    list_filter = (
        "warehouse",
        "product__unit",
    )

    search_fields = (
        "product__code",
        "product__name",
        "warehouse__code",
        "warehouse__name",
    )

    autocomplete_fields = (
        "warehouse",
        "product",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (
        (
            "موجودی",
            {
                "fields": (
                    "warehouse",
                    "product",
                    "quantity",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "updated_at",
                )
            },
        ),
    )

    ordering = (
        "warehouse",
        "product",
    )

    @admin.display(
        description="وضعیت",
        ordering="quantity",
    )
    def stock_status(self, obj):

        if obj.quantity <= 0:
            return format_html(
                '<strong style="color:#dc2626;">ناموجود</strong>'
            )

        if obj.quantity <= obj.product.minimum_stock:
            return format_html(
                '<strong style="color:#d97706;">موجودی کم</strong>'
            )

        return format_html(
            '<strong style="color:#16a34a;">موجود</strong>'
        )


# =========================================================
# اقلام درخواست انبار
# =========================================================

class WarehouseRequestItemInline(admin.TabularInline):

    model = WarehouseRequestItem

    extra = 0

    fields = (
        "execution_item",
        "product",
        "requested_quantity",
        "available_quantity",
        "delivered_quantity",
        "shortage_quantity",
        "description",
    )

    # -----------------------------------------------------
    # ExecutionItem در Admin ثبت نشده
    # بنابراین autocomplete نباید استفاده شود.
    # -----------------------------------------------------

    raw_id_fields = (
        "execution_item",
    )

    # Product در Admin ثبت شده
    autocomplete_fields = (
        "product",
    )

    ordering = (
        "execution_item__item_number",
    )


# =========================================================
# درخواست انبار
# =========================================================

@admin.register(WarehouseRequest)
class WarehouseRequestAdmin(admin.ModelAdmin):

    list_display = (
        "request_number",
        "project_name",
        "warehouse",
        "warehouse_manager",
        "status_display",
        "requested_at",
        "reviewed_at",
        "delivered_at",
    )

    list_filter = (
        "status",
        "warehouse",
        "requested_at",
        "reviewed_at",
        "delivered_at",
    )

    search_fields = (
        "request_number",
        "project_name",
        "execution__request_number",
        "execution__project_name",
        "warehouse__code",
        "warehouse__name",
        "warehouse_manager__username",
        "warehouse_manager__first_name",
        "warehouse_manager__last_name",
        "description",
        "shortage_description",
    )

    # -----------------------------------------------------
    # ارتباط با مدل‌های ERP
    # -----------------------------------------------------

    autocomplete_fields = (
        "execution",
        "warehouse",
    )

    # -----------------------------------------------------
    # User
    # -----------------------------------------------------

    raw_id_fields = (
        "warehouse_manager",
    )

    inlines = (
        WarehouseRequestItemInline,
    )

    readonly_fields = (
        "request_number",
        "project_name",
        "requested_at",
        "reviewed_at",
        "delivered_at",
    )

    fieldsets = (

        # =================================================
        # ارتباط با اجرایات
        # =================================================

        (
            "ارتباط با اجرایات",
            {
                "fields": (
                    "execution",
                    "request_number",
                    "project_name",
                )
            },
        ),

        # =================================================
        # اطلاعات انبار
        # =================================================

        (
            "اطلاعات انبار",
            {
                "fields": (
                    "warehouse",
                    "warehouse_manager",
                    "status",
                )
            },
        ),

        # =================================================
        # توضیحات
        # =================================================

        (
            "توضیحات",
            {
                "fields": (
                    "description",
                    "shortage_description",
                )
            },
        ),

        # =================================================
        # تاریخ‌ها
        # =================================================

        (
            "تاریخ و ساعت گردش",
            {
                "fields": (
                    "requested_at",
                    "reviewed_at",
                    "delivered_at",
                )
            },
        ),
    )

    ordering = (
        "-requested_at",
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
            "PENDING": "#2563eb",
            "AVAILABLE": "#16a34a",
            "PARTIAL": "#d97706",
            "DELIVERED": "#15803d",
            "REJECTED": "#dc2626",
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


# =========================================================
# گردش انبار
# =========================================================

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "warehouse",
        "transaction_type_display",
        "quantity",
        "warehouse_request",
        "created_by",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "warehouse",
        "created_at",
    )

    search_fields = (
        "product__code",
        "product__name",
        "warehouse__code",
        "warehouse__name",
        "warehouse_request__request_number",
        "created_by__username",
        "created_by__first_name",
        "created_by__last_name",
    )

    autocomplete_fields = (
        "warehouse",
        "product",
        "warehouse_request",
    )

    # User autocomplete نداریم
    raw_id_fields = (
        "created_by",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            "اطلاعات گردش",
            {
                "fields": (
                    "warehouse",
                    "product",
                    "warehouse_request",
                    "transaction_type",
                    "quantity",
                )
            },
        ),
        (
            "ثبت‌کننده",
            {
                "fields": (
                    "created_by",
                    "created_at",
                )
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="نوع تراکنش",
        ordering="transaction_type",
    )
    def transaction_type_display(self, obj):

        return obj.get_transaction_type_display()

