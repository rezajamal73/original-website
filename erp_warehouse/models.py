
from django.db import models
from django.contrib.auth import get_user_model

from erp_execution.models import ExecutionRequest, ExecutionItem


User = get_user_model()


# =========================================================
# انبار
# =========================================================

class Warehouse(models.Model):

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد انبار",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="نام انبار",
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="managed_warehouses",
        verbose_name="انباردار",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "انبار"
        verbose_name_plural = "انبارها"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================================================
# کالا
# =========================================================

class Product(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد کالا",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="نام کالا",
    )

    unit = models.CharField(
        max_length=30,
        default="عدد",
        verbose_name="واحد",
    )

    minimum_stock = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="حداقل موجودی",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================================================
# موجودی انبار
# =========================================================

class Stock(models.Model):

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stocks",
        verbose_name="کالا",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="موجودی",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "موجودی انبار"
        verbose_name_plural = "موجودی انبارها"
        ordering = ["warehouse", "product"]

        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"],
                name="unique_warehouse_product_stock",
            )
        ]

    def __str__(self):
        return (
            f"{self.warehouse.name} - "
            f"{self.product.name} - "
            f"{self.quantity}"
        )


# =========================================================
# درخواست انبار
# =========================================================

class WarehouseRequest(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "در انتظار بررسی"),
        ("AVAILABLE", "موجود و تأیید شد"),
        ("PARTIAL", "کسری موجودی"),
        ("DELIVERED", "تحویل شد"),
        ("REJECTED", "رد شد"),
    ]

    # =====================================================
    # اتصال به اجرایات
    # =====================================================

    execution = models.OneToOneField(
        ExecutionRequest,
        on_delete=models.PROTECT,
        related_name="warehouse_request",
        verbose_name="درخواست اجرایات",
    )

    # =====================================================
    # اطلاعات اصلی
    # =====================================================

    request_number = models.CharField(
        max_length=50,
        verbose_name="شماره درخواست",
    )

    project_name = models.CharField(
        max_length=200,
        verbose_name="نام پروژه",
    )

    warehouse_manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="warehouse_requests_managed",
        verbose_name="انباردار",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name="انبار",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="وضعیت",
    )

    # =====================================================
    # توضیحات
    # =====================================================

    description = models.TextField(
        blank=True,
        verbose_name="شرح درخواست",
    )

    shortage_description = models.TextField(
        blank=True,
        verbose_name="شرح کسری",
    )

    # =====================================================
    # زمان‌ها
    # =====================================================

    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت درخواست",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت بررسی",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت تحویل",
    )

    class Meta:
        verbose_name = "درخواست انبار"
        verbose_name_plural = "درخواست‌های انبار"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.request_number} - {self.project_name}"

    def save(self, *args, **kwargs):

        if self.execution_id:

            self.request_number = self.execution.request_number
            self.project_name = self.execution.project_name

            if not self.description:
                self.description = (
                    self.execution.execution_description
                    or self.execution.requester_description
                    or self.execution.description
                )

        super().save(*args, **kwargs)


# =========================================================
# اقلام درخواست انبار
# =========================================================

class WarehouseRequestItem(models.Model):

    warehouse_request = models.ForeignKey(
        WarehouseRequest,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="درخواست انبار",
    )

    execution_item = models.ForeignKey(
        ExecutionItem,
        on_delete=models.PROTECT,
        related_name="warehouse_items",
        verbose_name="قلم اجرایات",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="warehouse_request_items",
        verbose_name="کالا",
    )

    requested_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="تعداد درخواستی",
    )

    available_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="موجودی قابل تحویل",
    )

    delivered_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد تحویل‌شده",
    )

    shortage_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد کسری",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    class Meta:
        verbose_name = "قلم درخواست انبار"
        verbose_name_plural = "اقلام درخواست انبار"

        ordering = [
            "warehouse_request",
            "execution_item__item_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "warehouse_request",
                    "execution_item",
                ],
                name="unique_warehouse_execution_item",
            )
        ]

    def __str__(self):
        return (
            f"{self.warehouse_request.request_number} - "
            f"{self.product.name}"
        )

    def calculate_shortage(self):

        shortage = (
            self.requested_quantity
            - self.delivered_quantity
        )

        return max(shortage, 0)


# =========================================================
# گردش انبار
# =========================================================

class StockTransaction(models.Model):

    TRANSACTION_TYPES = [
        ("IN", "ورود"),
        ("OUT", "خروج"),
        ("ADJUSTMENT", "اصلاح موجودی"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        verbose_name="کالا",
    )

    warehouse_request = models.ForeignKey(
        WarehouseRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="درخواست انبار",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name="نوع تراکنش",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="تعداد",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="stock_transactions_created",
        verbose_name="ثبت‌کننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت",
    )

    class Meta:
        verbose_name = "گردش انبار"
        verbose_name_plural = "گردش انبارها"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.quantity} - "
            f"{self.get_transaction_type_display()}"
        )

