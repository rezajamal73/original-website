# app/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels


# ---------------------------------------
#   GLOBAL UNIQUE SLUG GENERATOR
# ---------------------------------------
def generate_unique_slug(instance, value, slug_field_name="slug"):
    """
    ایجاد اسلاگ یکتا برای یک instance.
    - value: متنِ پایه برای اسلاگ (مثلاً title_en یا title_fa)
    - خروجی: اسلاگ یکتا (اگر تکراری شد، با -1, -2, ... ادامه می‌یابد)
    """
    base_slug = slugify(value) or "item"
    slug = base_slug
    ModelClass = instance.__class__
    counter = 1

    # exclude current instance to allow update بدون تصادم با خودش
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
    slug = models.SlugField(unique=True, blank=True, editable=False)

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی مزایده"
        verbose_name_plural = "دسته‌بندی‌های مزایده"
        ordering = ["-created_at_fa"]

    def _get_slug_source(self):
        """اولویت: title_en سپس title_fa"""
        return self.title_en or self.title_fa or ""

    def save(self, *args, **kwargs):

        source = self._get_slug_source()
        base = slugify(source) or "item"
        if not self.slug:
            self.slug = generate_unique_slug(self, source)
        else:
            current_base = self.slug.split("-")[0]
            if current_base != base:
                self.slug = generate_unique_slug(self, source)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ---------------------------
#  Tags (Auction)
# ---------------------------
class AuctionTag(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")
    slug = models.SlugField(unique=True, blank=True, editable=False)

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "برچسب مزایده"
        verbose_name_plural = "برچسب‌های مزایده"
        ordering = ["-created_at_fa"]

    def _get_slug_source(self):
        return self.title_en or self.title_fa or ""

    def save(self, *args, **kwargs):
        source = self._get_slug_source()
        base = slugify(source) or "item"
        if not self.slug:
            self.slug = generate_unique_slug(self, source)
        else:
            current_base = self.slug.split("-")[0]
            if current_base != base:
                self.slug = generate_unique_slug(self, source)
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
    slug = models.SlugField(unique=True, blank=True, editable=False)
    call_number = models.CharField(max_length=100, unique=True, verbose_name="شماره فراخوان")
    start_date_fa = jmodels.jDateField(verbose_name="تاریخ شروع (شمسی)", help_text="1373-08-10")
    end_date_fa = jmodels.jDateField(verbose_name="تاریخ پایان (شمسی)", help_text="1373-08-10")
    start_date_en = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_en = models.DateField(verbose_name="تاریخ پایان (میلادی)")
    poster = models.ImageField(upload_to='auction/posters',verbose_name="تصویر")
    upload_file = models.FileField(upload_to='blog/upload_file', null=True, blank=True, verbose_name="آپلود فایل")
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

    def _get_slug_source(self):
        return self.title_en or self.title_fa or ""

    def save(self, *args, **kwargs):
        source = self._get_slug_source()
        base = slugify(source) or "item"
        if not self.slug:
            self.slug = generate_unique_slug(self, source)
        else:
            current_base = self.slug.split("-")[0]
            if current_base != base:
                self.slug = generate_unique_slug(self, source)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title_fa} - {self.call_number}"


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

    image = models.ImageField(upload_to="auction/gallery", verbose_name="تصویر")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح عکس")

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "عکس گالری"
        verbose_name_plural = "گالری"
        ordering = ("order",)

    def __str__(self):
        return self.caption or "Image"
