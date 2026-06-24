from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse

# QR Code
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


# ============================================================
# UNIQUE SLUG GENERATOR
# ============================================================
def generate_unique_slug(instance, slug_field: str, text_value: str):
    base_slug = slugify(text_value) or "item"
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
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی", blank=True)

    cat_icon = models.FileField(
        "آیکون (SVG)",
        upload_to="products/category_icons/",
        blank=True,
        null=True
    )

    slug = models.SlugField(unique=True, blank=True)
    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "شکل دارویی"
        verbose_name_plural = "شکل دارویی"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        base = self.title_en or self.title_fa
        if not self.slug or slugify(self.slug) != slugify(base):
            self.slug = generate_unique_slug(self, "slug", base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ============================================================
# CATEGORY 2
# ============================================================
class ProductCategory2(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی", blank=True)

    slug = models.SlugField(unique=True, blank=True)
    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "دسته بندی دارویی"
        verbose_name_plural = "دسته بندی دارویی"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        base = self.title_en or self.title_fa
        if not self.slug or slugify(self.slug) != slugify(base):
            self.slug = generate_unique_slug(self, "slug", base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ============================================================
# TAG MODEL
# ============================================================
class ProductTag(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی", blank=True)

    slug = models.SlugField(unique=True, blank=True)
    priority = models.IntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "برچسب دارویی"
        verbose_name_plural = "برچسب‌های دارویی"
        ordering = ["priority", "title_fa"]

    def save(self, *args, **kwargs):
        base = self.title_en or self.title_fa
        if not self.slug or slugify(self.slug) != slugify(base):
            self.slug = generate_unique_slug(self, "slug", base)
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

    # دسته‌بندی اصلی
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="شکل دارویی",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    #دسته‌بندی دوم
    category2 = models.ForeignKey(
        ProductCategory2,
        verbose_name="دسته بندی دارویی",
        related_name="products2",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(ProductTag, verbose_name="برچسب‌ها", blank=True)

    title_fa = models.CharField("نام محصول (فارسی)", max_length=255)
    title_en = models.CharField("نام محصول-برند (انگلیسی)", max_length=255, blank=True)
    summary_fa = models.TextField("توضیح کوتاه (فارسی)", blank=True)
    summary_en = models.TextField("توضیح کوتاه (انگلیسی)", blank=True)
    slug = models.SlugField("اسلاگ", max_length=255, unique=True, blank=True)
    special = models.BooleanField("محصول ویژه", default=False)
    main_image = models.ImageField("تصویر اصلی", upload_to="products/main/", blank=True, null=True)
    qr_code = models.ImageField("QR code", upload_to="products/qr/", blank=True, null=True)
    qr_data = models.CharField("QR data", max_length=255, blank=True)
    generic_name_fa = models.CharField("نام ژنریک (فارسی)", max_length=255, blank=True)
    generic_name_en = models.CharField("نام ژنریک (انگلیسی)", max_length=255, blank=True)
    composition_fa = models.TextField("ترکیبات (فارسی)", blank=True)
    composition_en = models.TextField("ترکیبات (انگلیسی)", blank=True)
    indications_fa = models.TextField("موارد مصرف (فارسی)", blank=True)
    indications_en = models.TextField("موارد مصرف (انگلیسی)", blank=True)
    contra_fa = models.TextField("موارد منع مصرف (فارسی)", blank=True)
    contra_en = models.TextField("موارد منع مصرف (انگلیسی)", blank=True)
    warnings_fa = models.TextField("هشدارها (فارسی)", blank=True)
    warnings_en = models.TextField("هشدارها (انگلیسی)", blank=True)
    pregnancy_use_fa = models.TextField("مصرف در بارداری (فارسی)", blank=True)
    pregnancy_use_en = models.TextField("مصرف در بارداری (انگلیسی)", blank=True)
    instructions_fa = models.TextField("نحوه مصرف (فارسی)", blank=True)
    instructions_en = models.TextField("نحوه مصرف (انگلیسی)", blank=True)
    interactions_fa = models.TextField("تداخلات (فارسی)", blank=True)
    interactions_en = models.TextField("تداخلات (انگلیسی)", blank=True)
    description_fa = models.TextField("توضیحات (فارسی)", blank=True)
    description_en = models.TextField("توضیحات (انگلیسی)", blank=True)
    sku = models.CharField("کد محصول", max_length=128)
    priority = models.IntegerField("ترتیب نمایش", default=0)

    created_at = models.DateTimeField("ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("ویرایش", auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت"
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['priority', 'title_fa']


    def get_absolute_url(self):
        return reverse("app_product:product_single", kwargs={"pid": self.id})

    def __str__(self):
        return self.title_fa

    # جهت جلوگیری از محصول بدون نام
    def clean(self):
        if not self.title_fa and not self.title_en:
            raise ValidationError("نام محصول باید وارد شود.")

    # ساخت QR DATA
    def _build_qr_data(self):
        identifier = self.sku if self.sku else str(self.id)
        return f"PRODUCT:{identifier}"

    # ساخت تصویر QR
    def _generate_qr_image(self, data, filename):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=filename)

    # ذخیره محصول + ساخت QR
    def save(self, *args, **kwargs):
        base = self.title_en or self.title_fa

        if not self.slug or slugify(self.slug) != slugify(base):
            self.slug = generate_unique_slug(self, "slug", base)

        super().save(*args, **kwargs)

        desired_qr = self._build_qr_data()
        if self.qr_data != desired_qr:
            filename = f"qr_{self.slug or self.id}.png"
            content = self._generate_qr_image(desired_qr, filename)
            self.qr_code.save(filename, content, save=False)
            self.qr_data = desired_qr
            super().save(update_fields=['qr_code', 'qr_data'])

    def get_absolute_url(self):
        return reverse('app_product:product_single', kwargs={'pid': self.pk})


# ============================================================
# PRODUCT IMAGE
# ============================================================
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField("عکس", upload_to="products/gallery/")
    order = models.PositiveSmallIntegerField("ترتیب", default=0)
    uploaded_at = models.DateTimeField("آپلود", auto_now_add=True)

    class Meta:
        verbose_name = "عکس محصول"
        verbose_name_plural = "گالری محصولات"
        ordering = ['order', 'uploaded_at']

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
        on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=512, blank=True)
    scanned_at = models.DateTimeField("زمان اسکن", auto_now_add=True)

    class Meta:
        verbose_name = "اسکن محصول"
        verbose_name_plural = "اسکن محصولات"
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.product.title_fa} — {self.scanned_at}"
