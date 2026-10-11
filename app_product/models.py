# app_product/models.py
from functools import partial

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse

from django.conf import settings
# QR Code
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


# ============================================================
# DYNAMIC APP-BASED UPLOAD PATH
# ============================================================
def app_upload_to(instance, filename, subfolder=""):
    """
    ساخت مسیر آپلود به صورت داینامیک بر اساس نام اپ مدل.
    نتیجه: <app_label>/<subfolder>/<filename>
    """
    app_label = instance._meta.app_label
    return f"{app_label}/{subfolder}/{filename}".replace("//", "/")


# ============================================================
# UNIQUE SLUG GENERATOR
# ============================================================
def generate_unique_slug(instance, slug_field: str, text_value: str):
    """
    تولید اسلاگ یکتا با پشتیبانی از حروف فارسی.
    """
    base_slug = slugify(text_value, allow_unicode=True) or "item"
    slug = base_slug
    Model = instance.__class__
    counter = 1

    while Model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# ============================================================
# CATEGORY 1
# ============================================================
class ProductCategory(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ media/<app_label>/category_icons/...
    cat_icon = models.FileField(
        "آیکون (SVG)",
        upload_to=partial(app_upload_to, subfolder="category_icons"),
        blank=True,
        null=True,
    )

    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )

    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "شکل محصول"
        verbose_name_plural = "شکل محصول"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        if self.title_fa:
            expected = slugify(self.title_fa, allow_unicode=True) or "item"
            if not self.slug or not self.slug.startswith(expected):
                self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if self.title_en:
            expected_en = slugify(self.title_en, allow_unicode=False) or "item"
            if not self.slug_en or not self.slug_en.startswith(expected_en):
                self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ============================================================
# CATEGORY 2
# ============================================================
class ProductCategory2(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی", blank=True)

    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        if self.title_fa:
            expected = slugify(self.title_fa, allow_unicode=True) or "item"
            if not self.slug or not self.slug.startswith(expected):
                self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if self.title_en:
            expected_en = slugify(self.title_en, allow_unicode=False) or "item"
            if not self.slug_en or not self.slug_en.startswith(expected_en):
                self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ============================================================
# TAG MODEL
# ============================================================
class ProductTag(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        if self.title_fa:
            expected = slugify(self.title_fa, allow_unicode=True) or "item"
            if not self.slug or not self.slug.startswith(expected):
                self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if self.title_en:
            expected_en = slugify(self.title_en, allow_unicode=False) or "item"
            if not self.slug_en or not self.slug_en.startswith(expected_en):
                self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ============================================================
# PRODUCT MODEL
# ============================================================
class Product(models.Model):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    category = models.ForeignKey(
        ProductCategory,
        verbose_name="شکل محصول",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    category2 = models.ForeignKey(
        ProductCategory2,
        verbose_name="دسته بندی",
        related_name="products2",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(ProductTag, verbose_name="برچسب‌ها", blank=True)

    title_fa = models.CharField("نام محصول (فارسی)", max_length=255)
    title_en = models.CharField("نام محصول-برند (انگلیسی)", max_length=255)
    summary_fa = models.TextField("توضیح کوتاه (فارسی)", blank=True)
    summary_en = models.TextField("توضیح کوتاه (انگلیسی)", blank=True)

    slug = models.SlugField(
        "اسلاگ (فارسی)",
        max_length=255,
        unique=True,
        blank=True,
        allow_unicode=True,
    )

    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        max_length=255,
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    special = models.BooleanField("محصول ویژه", default=False)

    # ✅ media/<app_label>/main/...
    main_image = models.ImageField(
        "تصویر اصلی",
        upload_to=partial(app_upload_to, subfolder="main"),
        blank=True,
        null=True,
    )
    # ✅ media/<app_label>/qr/...
    qr_code = models.ImageField(
        "QR code",
        upload_to=partial(app_upload_to, subfolder="qr"),
        blank=True,
        null=True,
    )
    qr_data = models.CharField("QR data", max_length=255, blank=True)
    generic_name_fa = models.CharField("مدل (فارسی)", max_length=255, blank=True)
    generic_name_en = models.CharField("مدل (انگلیسی)", max_length=255, blank=True)

    description_1_fa = models.TextField("مشخصات فنی (فارسی)", blank=True)
    description_1_en = models.TextField("Description 1 (English)", blank=True)
    description_2_fa = models.TextField("قابلیت ها (فارسی)", blank=True)
    description_2_en = models.TextField("Description 2 (English)", blank=True)
    description_3_fa = models.TextField("رنگ بندی های موجود", blank=True)
    description_3_en = models.TextField("Description 3 (English)", blank=True)
    description_4_fa = models.TextField("رنگ بندی های سفارشی (فارسی)", blank=True)
    description_4_en = models.TextField("Description 4 (English)", blank=True)
    description_5_fa = models.TextField("توضیحات ۵ (فارسی)", blank=True)
    description_5_en = models.TextField("Description 5 (English)", blank=True)
    description_6_fa = models.TextField("توضیحات ۶ (فارسی)", blank=True)
    description_6_en = models.TextField("Description 6 (English)", blank=True)
    description_7_fa = models.TextField("توضیحات ۷ (فارسی)", blank=True)
    description_7_en = models.TextField("Description 7 (English)", blank=True)
    description_8_fa = models.TextField("توضیحات ۸ (فارسی)", blank=True)
    description_8_en = models.TextField("Description 8 (English)", blank=True)
    description_9_fa = models.TextField("توضیحات ۹ (فارسی)", blank=True)
    description_9_en = models.TextField("Description 9 (English)", blank=True)
    description_10_fa = models.TextField("توضیحات ۱۰ (فارسی)", blank=True)
    description_10_en = models.TextField("Description 10 (English)", blank=True)

    sku = models.CharField("کد محصول", max_length=128)
    priority = models.IntegerField("ترتیب نمایش", default=0)

    created_at = models.DateTimeField("ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("ویرایش", auto_now=True)

    # ✅ فیلدهای SEO حذف شدن — از app_seo استفاده کن

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["priority", "title_fa"]

    def __str__(self):
        return self.title_fa

    def clean(self):
        super().clean()

        if not self.title_fa and not self.title_en:
            raise ValidationError("نام محصول باید وارد شود.")

        if Product.objects.filter(sku=self.sku).exclude(pk=self.pk).exists():
            raise ValidationError({
                "sku": f"کد محصول {self.sku} وجود دارد."
            })

    # ============================================================
    # QR CODE
    # ============================================================
    def _build_qr_data(self):
        return settings.SITE_URL + reverse(
            "app_product:scan",
            kwargs={"sku": self.sku},
        )

    def _generate_qr_image(self, data, filename):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=filename)

    # ============================================================
    # SAVE
    # ============================================================
    def save(self, *args, **kwargs):
        self.full_clean()

        if self.title_fa:
            expected_fa = slugify(self.title_fa, allow_unicode=True) or "item"
            if not self.slug or not self.slug.startswith(expected_fa):
                self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if self.title_en:
            expected_en = slugify(self.title_en, allow_unicode=False) or "item"
            if not self.slug_en or not self.slug_en.startswith(expected_en):
                self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        # ✅ بلاک SEO حذف شد — از app_seo استفاده کن

        super().save(*args, **kwargs)

        # QR
        desired_qr = self._build_qr_data()
        if self.qr_data != desired_qr:
            filename = f"qr_{self.slug or self.id}.png"
            content = self._generate_qr_image(desired_qr, filename)
            self.qr_code.save(filename, content, save=False)
            self.qr_data = desired_qr
            super().save(update_fields=["qr_code", "qr_data"])

    # ============================================================
    # URL ها — ✅ بدون pid
    # ============================================================
    def get_absolute_url(self):
        """URL فارسی: /product/آویز-سرم-بیمارستانی/"""
        return reverse("app_product:product_single", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/product/hospital-iv-pole/"""
        return reverse("app_product_en:product_single_en", kwargs={
            "slug": self.slug_en,
        })


# ============================================================
# PRODUCT IMAGE
# ============================================================
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        related_name="images",
        on_delete=models.CASCADE,
    )
    # ✅ media/<app_label>/gallery/...
    image = models.ImageField(
        "عکس",
        upload_to=partial(app_upload_to, subfolder="gallery"),
    )
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    uploaded_at = models.DateTimeField("آپلود", auto_now_add=True)

    class Meta:
        verbose_name = "عکس محصول"
        verbose_name_plural = "گالری محصولات"
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image for {self.product} ({self.pk})"

    def clean(self):
        if not self.product_id:
            return
        if not self.pk:
            if ProductImage.objects.filter(product_id=self.product_id).count() >= 10:
                raise ValidationError("حداکثر ۱۰ تصویر مجاز است.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================================
# PRODUCT SCAN
# ============================================================
class ProductScan(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        related_name="scans",
        on_delete=models.CASCADE,
    )
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=512, blank=True)
    scanned_at = models.DateTimeField("زمان اسکن", auto_now_add=True)

    class Meta:
        verbose_name = "اسکن محصول"
        verbose_name_plural = "اسکن محصولات"
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.product.title_fa} — {self.scanned_at}"


# ============================================================
# PRODUCT COLOR
# ============================================================
class ProductColor(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="colors",
        on_delete=models.CASCADE,
        verbose_name="محصول",
    )

    title = models.CharField("نام رنگ", max_length=100, blank=True)
    color_code = models.CharField("کد رنگ", max_length=7, help_text="مثال: #FF0000")
    order = models.PositiveIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ‌های محصول"

    def __str__(self):
        return self.title or self.color_code