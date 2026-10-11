# app_blog/models.py
from functools import partial

from django.db import models
from django.utils.text import slugify
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
from django.urls import reverse


# -------------------------------------------------------
#   DYNAMIC APP-BASED UPLOAD PATH
# -------------------------------------------------------
def app_upload_to(instance, filename, subfolder=""):
    """
    ساخت مسیر آپلود به صورت داینامیک بر اساس نام اپ مدل.
    نتیجه: <app_label>/<subfolder>/<filename>
    """
    app_label = instance._meta.app_label
    return f"{app_label}/{subfolder}/{filename}".replace("//", "/")


# -------------------------------------------------------
#   تابع تولید اسلاگ یکتا
# -------------------------------------------------------
def unique_slugify(instance, value, slug_field_name='slug'):
    """تولید اسلاگ یکتا با پشتیبانی از فارسی"""
    base_slug = slugify(value, allow_unicode=True) or "item"
    Model = instance.__class__
    slug = base_slug
    counter = 1

    while Model.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class TimeStampedModel(models.Model):
    created_at_fa = models.DateTimeField(auto_now_add=True)
    updated_at_fa = models.DateTimeField(auto_now=True)

    created_at_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


# -------------------------------------------------------
#   CATEGORY (Sortable)
# -------------------------------------------------------
class blog_Category(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ("-created_at_fa", "order")

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = unique_slugify(self, self.title_fa, "slug")

        if not self.slug_en and self.title_en:
            self.slug_en = unique_slugify(self, self.title_en, "slug_en")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# -------------------------------------------------------
#   TAG (Sortable)
# -------------------------------------------------------
class blog_Tag(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ("-created_at_fa", "order")

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = unique_slugify(self, self.title_fa, "slug")
        if not self.slug_en and self.title_en:
            self.slug_en = unique_slugify(self, self.title_en, "slug_en")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# -------------------------------------------------------
#   BLOG
# -------------------------------------------------------
class blog(TimeStampedModel):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده")
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    # ✅ اسلاگ فارسی
    slug = models.SlugField(
        "اسلاگ (فارسی)",
        unique=True,
        blank=True,
        allow_unicode=True,
    )

    # ✅ اسلاگ انگلیسی
    slug_en = models.SlugField(
        "اسلاگ (انگلیسی)",
        unique=True,
        blank=True,
        allow_unicode=False,
    )

    # ✅ media/<app_label>/image/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="image"),
        default='blog/default.jpg',
        verbose_name="عکس اصلی",
    )
    # ✅ media/<app_label>/upload_file/...
    upload_file = models.FileField(
        upload_to=partial(app_upload_to, subfolder="upload_file"),
        null=True,
        blank=True,
        verbose_name="آپلود فایل",
    )
    category = models.ForeignKey(blog_Category, on_delete=models.CASCADE, related_name="blog", verbose_name="دسته‌بندی")
    tags = models.ManyToManyField(blog_Tag, related_name="blog", blank=True, verbose_name="برچسب‌ها")
    content_1_fa = models.TextField(verbose_name="متن فارسی 1")
    content_1_en = models.TextField(verbose_name="متن انگلیسی 1")
    content_2_fa = models.TextField(blank=True, verbose_name="متن فارسی 2")
    content_2_en = models.TextField(blank=True, verbose_name="متن انگلیسی 2")

    publish_date_fa = jmodels.jDateField(verbose_name="تاریخ انتشار (شمسی)", help_text="1373-08-10")
    publish_date_en = models.DateField(verbose_name="تاریخ انتشار (میلادی)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="وضعیت")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["order", "-publish_date_fa"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title_fa:
            self.slug = unique_slugify(self, self.title_fa, "slug")

        if not self.slug_en and self.title_en:
            self.slug_en = unique_slugify(self, self.title_en, "slug_en")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /blog/نام-مقاله/"""
        return reverse("app_blog:blog_single", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/blog/post-name/"""
        return reverse("app_blog_en:blog_single_en", kwargs={
            "slug": self.slug_en,
        })


# -------------------------------------------------------
#   BLOG IMAGE
# -------------------------------------------------------
class BlogImage(models.Model):
    blog = models.ForeignKey(blog, on_delete=models.CASCADE, related_name="images", verbose_name="مقاله")
    # ✅ media/<app_label>/gallery/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="gallery"),
        verbose_name="تصویر",
    )
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر مقاله"
        verbose_name_plural = "گالری"
        ordering = ["order", "id"]

    def __str__(self):
        return f"تصویر {self.blog.title_fa} - ترتیب {self.order}"