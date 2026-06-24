# app/models.py

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# ------------------------------------------------------
#   GENERIC UNIQUE SLUG MAKER (Reusable for all models)
# ------------------------------------------------------
def generate_unique_slug(instance, slug_field: str, text_value: str):
    base_slug = slugify(text_value) or "item"
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
    slug = models.SlugField(unique=True, blank=True, editable=False)
    summary_fa = models.TextField(verbose_name="متن قسمت اول فارسی")
    summary_en = models.TextField(verbose_name="متن قسمت اول انگلیسی")

    image = models.ImageField(
        upload_to="news/cover/",
        default="news/default.jpg",
        verbose_name="کاور خبر"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت"
    )

    is_special = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "رسانه"
        verbose_name_plural = "رسانه ها"
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.slug) != slugify(self.title_en):
            self.slug = generate_unique_slug(self, "slug", self.title_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ------------------------------------------------------
#   MEDIA IMAGE
# ------------------------------------------------------
class MediaImage(models.Model):
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="news/gallery/")
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
        related_name="videos"
    )
    video = models.FileField(upload_to="news/videos/")
    duration = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="مدت زمان ویدیو"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویدیوی رسانه"
        verbose_name_plural = "ویدیوهای رسانه"
        ordering = ["order", "id"]

    def __str__(self):
        return f"ویدیو {self.media.title_fa} - ترتیب {self.order}"
