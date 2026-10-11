# app_auction/models.py

from functools import partial

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from django_jalali.db import models as jmodels


# ---------------------------------------
#   DYNAMIC APP-BASED UPLOAD PATH
# ---------------------------------------
def app_upload_to(instance, filename, subfolder=""):
    """
    ساخت مسیر آپلود به صورت داینامیک بر اساس نام اپ مدل.
    نتیجه: app_auction/<subfolder>/<filename>
    """
    app_label = instance._meta.app_label  # مثلاً: app_auction
    return f"{app_label}/{subfolder}/{filename}".replace("//", "/")


# ---------------------------------------
#   GLOBAL UNIQUE SLUG GENERATOR
# ---------------------------------------
def generate_unique_slug(instance, value, slug_field_name="slug"):
    """
    ایجاد اسلاگ یکتا با پشتیبانی از فارسی.
    """
    base_slug = slugify(value, allow_unicode=True) or "item"
    slug = base_slug
    ModelClass = instance.__class__
    counter = 1

    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
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
#  Category (Auction)
# ---------------------------
class AuctionCategory(TimeStampedModel):
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
        verbose_name = "دسته‌بندی مزایده"
        verbose_name_plural = "دسته‌بندی‌های مزایده"
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
#  Tags (Auction)
# ---------------------------
class AuctionTag(TimeStampedModel):
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
        verbose_name = "برچسب مزایده"
        verbose_name_plural = "برچسب‌های مزایده"
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
#        Auction Model
# ---------------------------
class Auction(TimeStampedModel):
    STATUS_CHOICES = (
        ("ongoing", "در حال برگزاری"),
        ("extended", "تمدید شده"),
        ("finished", "پایان یافته"),
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

    call_number = models.CharField(max_length=100, unique=True, verbose_name="شماره فراخوان")
    start_date_fa = jmodels.jDateField(verbose_name="تاریخ شروع (شمسی)", help_text="1373-08-10")
    end_date_fa = jmodels.jDateField(verbose_name="تاریخ پایان (شمسی)", help_text="1373-08-10")
    start_date_en = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_en = models.DateField(verbose_name="تاریخ پایان (میلادی)")

    # ✅ مسیر آپلود داینامیک بر اساس نام اپ → media/app_auction/posters/...
    poster = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="posters"),
        verbose_name="تصویر",
    )
    # ✅ media/app_auction/upload_file/...
    upload_file = models.FileField(
        upload_to=partial(app_upload_to, subfolder="upload_file"),
        null=True,
        blank=True,
        verbose_name="آپلود فایل",
    )
    estimated_amount = models.BigIntegerField(null=True, blank=True, verbose_name="مبلغ ضمانت مزایده")

    category = models.ForeignKey(
        AuctionCategory,
        on_delete=models.CASCADE,
        related_name="auctions",
        verbose_name="دسته‌بندی"
    )

    tags = models.ManyToManyField(
        AuctionTag,
        related_name="auctions",
        blank=True,
        verbose_name="برچسب‌ها"
    )

    description_fa = models.TextField(verbose_name="توضیحات فارسی")
    description_en = models.TextField(verbose_name="توضیحات انگلیسی")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ongoing", verbose_name="وضعیت"
    )

    class Meta:
        ordering = ["-created_at_fa"]
        verbose_name = "مزایده"
        verbose_name_plural = "مزایده‌ها"

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, self.title_fa, "slug")
        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, self.title_en, "slug_en")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title_fa} - {self.call_number}"

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /auction/نام-مزایده/"""
        return reverse("app_auction:auction_single", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/auction/auction-name/"""
        return reverse("app_auction_en:auction_single_en", kwargs={
            "slug": self.slug_en,
        })


# ---------------------------
#   Gallery Images (Auction)
# ---------------------------
class AuctionImage(TimeStampedModel):
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="مزایده"
    )
    # ✅ media/app_auction/gallery/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="gallery"),
        verbose_name="تصویر",
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح عکس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "عکس گالری"
        verbose_name_plural = "گالری"
        ordering = ("order",)

    def __str__(self):
        return self.caption or "Image"