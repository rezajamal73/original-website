# app_inquiry/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse                          # ✅ اضافه شد
from django_jalali.db import models as jmodels


# ---------------------------------------
#   GLOBAL UNIQUE SLUG GENERATOR
# ---------------------------------------
def generate_unique_slug(instance, value, slug_field_name="slug"):
    """
    ایجاد اسلاگ یکتا با پشتیبانی از فارسی.
    """
    base_slug = slugify(value, allow_unicode=True) or "item"   # ✅ allow_unicode
    slug = base_slug
    ModelClass = instance.__class__
    counter = 1

    while ModelClass.objects.filter(
        **{slug_field_name: slug}
    ).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# ---------------------------
#  Base TimeStamped Model
# ---------------------------
class TimeStampedModel(models.Model):
    created_at_fa = models.DateTimeField(auto_now_add=True)
    updated_at_fa = models.DateTimeField(auto_now=True)

    created_at_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


# ---------------------------
#  Inquiry Category
# ---------------------------
class InquiryCategory(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=False,
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی استعلام خرید"
        verbose_name_plural = "دسته‌بندی‌های استعلام خرید"
        ordering = ["-created_at_fa"]

    def save(self, *args, **kwargs):
        # ✅ اسلاگ فارسی از title_fa
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, self.title_fa, "slug")

        # ✅ اسلاگ انگلیسی از title_en
        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, self.title_en, "slug_en")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ---------------------------
#  Inquiry Tags
# ---------------------------
class InquiryTag(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=False,
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "برچسب استعلام خرید"
        verbose_name_plural = "برچسب‌های استعلام خرید"
        ordering = ["-created_at_fa"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, self.title_fa, "slug")
        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, self.title_en, "slug_en")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ---------------------------
#   Purchase Inquiry Model
# ---------------------------
class PurchaseInquiry(TimeStampedModel):
    STATUS_CHOICES = (
        ("open", "در حال برگزاری"),
        ("extended", "تمدید شده"),
        ("closed", "پایان یافته"),
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        editable=False,
        allow_unicode=False,
    )

    inquiry_number = models.CharField(
        max_length=100, unique=True, verbose_name="شماره استعلام"
    )

    start_date_fa = jmodels.jDateField(
        verbose_name="تاریخ شروع (شمسی)",
        help_text="1373-08-10",
    )
    end_date_fa = jmodels.jDateField(
        verbose_name="تاریخ پایان (شمسی)",
        help_text="1373-08-10",
    )
    start_date_en = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_en = models.DateField(verbose_name="تاریخ پایان (میلادی)")

    cover_image = models.ImageField(
        upload_to="purchase/cover",
        verbose_name="تصویر",
    )
    attachment = models.FileField(
        upload_to="purchase/files",
        null=True,
        blank=True,
        verbose_name="فایل پیوست",
    )

    estimated_amount = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="مبلغ برآوردی",
    )

    category = models.ForeignKey(
        InquiryCategory,
        on_delete=models.CASCADE,
        related_name="inquiries",
        verbose_name="دسته‌بندی",
    )

    tags = models.ManyToManyField(
        InquiryTag,
        related_name="inquiries",
        blank=True,
        verbose_name="برچسب‌ها",
    )

    description_fa = models.TextField(verbose_name="توضیحات فارسی")
    description_en = models.TextField(verbose_name="توضیحات انگلیسی")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "استعلام خرید"
        verbose_name_plural = "استعلام‌های خرید"
        ordering = ["-created_at_fa"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, self.title_fa, "slug")
        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, self.title_en, "slug_en")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title_fa} - {self.inquiry_number}"

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /inquiry/5/نام/"""
        return reverse("app_inquiry:inquiry_single", kwargs={
            "pid": self.pk,
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/inquiry/5/name/"""
        return reverse("app_inquiry_en:inquiry_single_en", kwargs={
            "pid": self.pk,
            "slug": self.slug_en,
        })


# ---------------------------
#   Inquiry Gallery Images
# ---------------------------
class PurchaseInquiryImage(TimeStampedModel):
    inquiry = models.ForeignKey(
        PurchaseInquiry,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="استعلام خرید",
    )

    image = models.ImageField(
        upload_to="purchase/gallery",
        verbose_name="تصویر",
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="توضیح تصویر",
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر استعلام خرید"
        verbose_name_plural = "گالری تصاویر"
        ordering = ("order",)

    def __str__(self):
        return self.caption or "Image"