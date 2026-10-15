# app_news/models.py
from functools import partial

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django_jalali.db import models as jmodels
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
#   BASE MODEL (CREATED/UPDATED)
# ------------------------------------------------------
class TimeStampedModel(models.Model):
    created_at_fa = models.DateTimeField(auto_now_add=True)
    updated_at_fa = models.DateTimeField(auto_now=True)

    created_at_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


# ------------------------------------------------------
#   CATEGORY
# ------------------------------------------------------
class NewsCategory(TimeStampedModel):
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
        verbose_name = "دسته خبر"
        verbose_name_plural = "دسته‌های خبر"
        ordering = ["-id"]

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


# ------------------------------------------------------
#   TAG
# ------------------------------------------------------
class NewsTag(TimeStampedModel):
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

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ------------------------------------------------------
#   NEWS
# ------------------------------------------------------
class News(TimeStampedModel):
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

    content_fa = models.TextField(blank=True, verbose_name="متن قسمت دوم فارسی")
    content_en = models.TextField(blank=True, verbose_name="متن قسمت دوم انگلیسی")

    # ✅ media/<app_label>/cover/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="cover"),
        verbose_name="کاور خبر",
    )

    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.CASCADE,
        related_name="news",
        verbose_name="دسته‌بندی",
    )
    tags = models.ManyToManyField(
        NewsTag,
        related_name="news_tags",
        verbose_name="برچسب‌ها",
    )

    publish_date_fa = jmodels.jDateField(
        verbose_name="تاریخ انتشار (شمسی)",
        help_text="1373-08-10",
    )
    publish_date_en = models.DateField(verbose_name="تاریخ انتشار (میلادی)")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت",
    )
    is_special = models.BooleanField(default=False, verbose_name="خبر ویژه")

    source = models.CharField(max_length=255, null=True, blank=True, verbose_name="منبع خبر")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="محل وقوع خبر")

    views = models.PositiveIntegerField(default=0, verbose_name="بازدید")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"
        ordering = ["-publish_date_fa", "-id"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = generate_unique_slug(self, "slug", self.title_fa)

        if not self.slug_en and self.title_en:
            self.slug_en = generate_unique_slug(self, "slug_en", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa

    # =====================================================
    # URL ها — همیشه absolute (کامل با دامنه)
    # =====================================================
    def get_absolute_url(self):
        """
        URL کامل فارسی:
        https://nkavosh.com/news/عنوان-خبر/
        """
        path = reverse("app_news:news_single", kwargs={
            "slug": self.slug,
        })
        site_url = getattr(settings, "SITE_URL", "").rstrip("/")
        if site_url:
            return f"{site_url}{path}"
        return path

    def get_absolute_url_en(self):
        """
        URL کامل انگلیسی:
        https://nkavosh.com/en/news/news-title/
        """
        path = reverse("app_news_en:news_single_en", kwargs={
            "slug": self.slug_en,
        })
        site_url = getattr(settings, "SITE_URL", "").rstrip("/")
        if site_url:
            return f"{site_url}{path}"
        return path


# ------------------------------------------------------
#   NEWS IMAGE
# ------------------------------------------------------
class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="images")
    # ✅ media/<app_label>/gallery/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="gallery"),
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر خبر"
        verbose_name_plural = "عکس‌های خبر"
        ordering = ["order", "id"]

    def __str__(self):
        return f"تصویر {self.news.title_fa} - ترتیب {self.order}"


# ------------------------------------------------------
#   NEWS VIDEO
# ------------------------------------------------------
class NewsVideo(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="videos")
    # ✅ media/<app_label>/videos/...
    video = models.FileField(
        upload_to=partial(app_upload_to, subfolder="videos"),
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح ویدیو")
    duration = models.CharField(max_length=10, blank=True, null=True, verbose_name="مدت زمان ویدیو")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویدیوی خبر"
        verbose_name_plural = "ویدیوهای خبر"
        ordering = ["order", "id"]

    def __str__(self):
        return f"ویدیو {self.news.title_fa} - ترتیب {self.order}"