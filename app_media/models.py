# app_media/models.py
from functools import partial

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User


# ------------------------------------------------------
#   DYNAMIC APP-BASED UPLOAD PATH
# ------------------------------------------------------
def app_upload_to(instance, filename, subfolder=""):
    """
    ساخت مسیر آپلود به صورت داینامیک بر اساس نام اپ مدل.
    نتیجه: <app_label>/<subfolder>/<filename>
    """
    app_label = instance._meta.app_label
    return f"{app_label}/{subfolder}/{filename}".replace("//", "/")


# ------------------------------------------------------
#   GENERIC UNIQUE SLUG MAKER (Reusable for all models)
# ------------------------------------------------------
def generate_unique_slug(instance, slug_field: str, text_value: str):
    """
    تولید اسلاگ یکتا با پشتیبانی از فارسی.
    """
    base_slug = slugify(text_value, allow_unicode=True) or "item"
    slug = base_slug
    Model = instance.__class__
    counter = 1

    while Model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# ------------------------------------------------------
#   MEDIA
# ------------------------------------------------------
class Media(models.Model):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

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

    summary_fa = models.TextField(verbose_name="متن قسمت اول فارسی")
    summary_en = models.TextField(verbose_name="متن قسمت اول انگلیسی")

    # ✅ media/<app_label>/cover/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="cover"),
        default="media/default.jpg",
        verbose_name="کاور رسانه",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت",
    )

    is_special = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "رسانه"
        verbose_name_plural = "رسانه‌ها"
        ordering = ["order"]

    def save(self, *args, **kwargs):
        # ✅ اسلاگ فارسی از title_fa
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, "slug", self.title_fa)

        # ✅ اسلاگ انگلیسی از title_en
        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /media/عنوان/"""
        return reverse("app_media:media_single", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/media/media-title/"""
        return reverse("app_media_en:media_single_en", kwargs={
            "slug": self.slug_en,
        })


# ------------------------------------------------------
#   MEDIA IMAGE
# ------------------------------------------------------
class MediaImage(models.Model):
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="رسانه",
    )
    # ✅ media/<app_label>/gallery/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="gallery"),
        verbose_name="تصویر",
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر رسانه"
        verbose_name_plural = "تصاویر رسانه"
        ordering = ["order", "id"]

    def __str__(self):
        return f"تصویر {self.media.title_fa} - ترتیب {self.order}"


# ------------------------------------------------------
#   MEDIA VIDEO
# ------------------------------------------------------
class MediaVideo(models.Model):
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="رسانه",
    )
    # ✅ media/<app_label>/videos/...
    video = models.FileField(
        upload_to=partial(app_upload_to, subfolder="videos"),
        verbose_name="ویدیو",
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح ویدیو")
    duration = models.CharField(max_length=10, blank=True, null=True, verbose_name="مدت زمان ویدیو")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویدیوی رسانه"
        verbose_name_plural = "ویدیوهای رسانه"
        ordering = ["order", "id"]

    def __str__(self):
        return f"ویدیو {self.media.title_fa} - ترتیب {self.order}"