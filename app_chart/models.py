# app_chart/models.py
from functools import partial

from django.db import models
from django.utils.text import slugify
from django.utils.html import format_html
from django.urls import reverse


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


# ============================================================
# PERSON (چارت سازمانی)
# ============================================================
class Person(models.Model):
    name_fa = models.CharField("نام و نام خانوادگی (فارسی)", max_length=200)
    name_en = models.CharField("نام و نام خانوادگی (انگلیسی)", max_length=200, blank=True)

    position_fa = models.CharField("سمت (فارسی)", max_length=200)
    position_en = models.CharField("سمت (انگلیسی)", max_length=200, blank=True)

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

    # ✅ media/<app_label>/photos/...
    photo = models.ImageField(
        "عکس",
        upload_to=partial(app_upload_to, subfolder="photos"),
    )

    parent = models.ForeignKey(
        "self",
        verbose_name="والد / سرپرست",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    order = models.PositiveIntegerField("ترتیب در زیرمجموعه", default=0)

    phone = models.CharField("تلفن", max_length=64, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    content_en = models.TextField(blank=True, verbose_name="متن انگلیسی")
    content_fa = models.TextField(blank=True, verbose_name="متن فارسی")

    is_ceo = models.BooleanField("مدیرعامل", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "چارت سازمانی"
        verbose_name_plural = "چارت سازمانی کلی"
        ordering = ["parent__id", "order", "name_fa"]

    def save(self, *args, **kwargs):
        # ✅ اسلاگ فارسی از name_fa
        if not self.slug and self.name_fa:
            self.slug = generate_unique_slug(self, "slug", self.name_fa)

        # ✅ اسلاگ انگلیسی از name_en
        if not self.slug_en and self.name_en:
            self.slug_en = generate_unique_slug(self, "slug_en", self.name_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_fa} — {self.position_fa}"

    def photo_tag(self):
        if self.photo:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;" />',
                self.photo.url,
            )
        return "(No photo)"

    photo_tag.short_description = "عکس"
    photo_tag.allow_tags = True

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /chart/person/نام-فرد/"""
        return reverse("app_chart:person_detail", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/chart/person/person-name/"""
        return reverse("app_chart_en:person_detail_en", kwargs={
            "slug": self.slug_en,
        })


# ============================================================
# BOARD MEMBER (هیأت‌مدیره)
# ============================================================
class BoardMember(models.Model):
    name_fa = models.CharField("نام و نام خانوادگی (فارسی)", max_length=200)
    name_en = models.CharField("نام و نام خانوادگی (انگلیسی)", max_length=200, blank=True)

    position_fa = models.CharField("سمت (فارسی)", max_length=200)
    position_en = models.CharField("سمت (انگلیسی)", max_length=200, blank=True)

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

    # ✅ media/<app_label>/photos/...
    photo = models.ImageField(
        "عکس",
        upload_to=partial(app_upload_to, subfolder="photos"),
    )

    parent = models.ForeignKey(
        "self",
        verbose_name="والد / سرپرست",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    order = models.PositiveIntegerField("ترتیب در زیرمجموعه", default=0)

    phone = models.CharField("تلفن", max_length=64, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    content_en = models.TextField(blank=True, verbose_name="متن انگلیسی")
    content_fa = models.TextField(blank=True, verbose_name="متن فارسی")

    is_ceo = models.BooleanField("رئیس هیأت‌مدیره", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عضو هیأت‌مدیره"
        verbose_name_plural = "اعضای هیأت‌مدیره"
        ordering = ["parent__id", "order", "name_fa"]

    def save(self, *args, **kwargs):
        # ✅ اسلاگ فارسی از name_fa
        if not self.slug and self.name_fa:
            self.slug = generate_unique_slug(self, "slug", self.name_fa)

        # ✅ اسلاگ انگلیسی از name_en
        if not self.slug_en and self.name_en:
            self.slug_en = generate_unique_slug(self, "slug_en", self.name_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_fa} — {self.position_fa}"

    def photo_tag(self):
        if self.photo:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;" />',
                self.photo.url,
            )
        return "(No photo)"

    photo_tag.short_description = "عکس"
    photo_tag.allow_tags = True

    # =====================================================
    # URL ها
    # =====================================================
    def get_absolute_url(self):
        """URL فارسی: /chart/board/نام-عضو/"""
        return reverse("app_chart:board_single", kwargs={
            "slug": self.slug,
        })

    def get_absolute_url_en(self):
        """URL انگلیسی: /en/chart/board/member-name/"""
        return reverse("app_chart_en:board_single_en", kwargs={
            "slug": self.slug_en,
        })