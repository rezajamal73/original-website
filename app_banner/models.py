from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class HeroSliderSetting(models.Model):

    HERO_TYPE_CHOICES = (
        ("hs_1", "اسلایدر مدل ۱(کوچک،وسط)"),
        ("hs_2", "اسلایدر مدل ۲(تمام صفحه)"),
    )

    active_slider = models.CharField(
        max_length=10,
        choices=HERO_TYPE_CHOICES,
        default="hs_1",
        verbose_name="مدل اسلایدر فعال صفحه اصلی"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات اسلایدر صفحه اصلی"
        verbose_name_plural = "تنظیمات اسلایدر صفحه اصلی"

    def clean(self):
        if not self.pk and HeroSliderSetting.objects.exists():
            raise ValidationError("فقط یک تنظیمات اسلایدر می‌تواند وجود داشته باشد.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "تنظیمات اسلایدر صفحه اصلی"
# ============================================================
#   بنر اصلی (اسلایدر صفحه خانه)
# ============================================================
class HeroBanner(models.Model):

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    order = models.PositiveIntegerField(
        default=0, verbose_name="اولویت نمایش"
    )

    # ---------- فارسی ----------
    label_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="برچسب (فارسی)"
    )
    title_p1_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان اول (فارسی)"
    )
    title_p2_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان دوم رنگ متفاوت (فارسی)"
    )
    title_p3_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان سوم (فارسی)"
    )
    subtitle_fa = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="زیرعنوان (فارسی)"
    )

    # ---------- انگلیسی ----------
    label_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="برچسب (انگلیسی)"
    )
    title_p1_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان اول (انگلیسی)"
    )
    title_p2_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان دوم رنگ متفاوت (انگلیسی)"
    )
    title_p3_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان سوم (انگلیسی)"
    )
    subtitle_en = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="زیرعنوان (انگلیسی)"
    )

    slug = models.SlugField(
        unique=True, blank=True, verbose_name="اسلاگ"
    )

    image = models.ImageField(
        upload_to="banner/image/", verbose_name="تصویر بنر"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="draft", verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "بنر های اصلی پوستر"
        verbose_name_plural = "بنر های اصلی پوستر "
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.title_p1_en or self.label_en or "hero-banner"
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label_fa or self.title_p1_fa or f"بنر اسلایدر #{self.pk}"


# ============================================================
#   بنر صفحات داخلی
# ============================================================
class OtherBanner(models.Model):

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    order = models.PositiveIntegerField(default=0, verbose_name="اولویت نمایش")

    label_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان بنر"
    )

    slug = models.SlugField(unique=True, blank=True, verbose_name="اسلاگ")

    image = models.ImageField(
        upload_to="banner/image/", verbose_name="تصویر بنر"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="draft", verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "بنر هدرِ کل صفحات"
        verbose_name_plural = "بنر هدرِ کل"
        ordering = ("order",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f"other-banner-{self.pk}"
            super().save(update_fields=["slug"])

    def __str__(self):
        return self.label_fa or f"بنر داخلی #{self.pk}"


# ============================================================
#   بنر محصولات ویژه (فقط یک فعال)
# ============================================================
class SpecialProductBanner(models.Model):

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    title_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان بنر"
    )

    slug = models.SlugField(unique=True, blank=True, verbose_name="اسلاگ")

    image = models.ImageField(
        upload_to="banners/special-products/", verbose_name="تصویر بنر"
    )

    order = models.PositiveSmallIntegerField(default=0, verbose_name="اولویت نمایش")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="draft", verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "بنر محصول ویژه"
        verbose_name_plural = "بنر محصولات ویژه"
        ordering = ("order", "created_at")

    def clean(self):
        if self.status == "published":
            qs = SpecialProductBanner.objects.filter(status="published")
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("فقط یک بنر محصول ویژه می‌تواند فعال باشد.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_fa or "special-product-banner")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa or f"بنر محصول ویژه #{self.pk}"


# ============================================================
#   بنر اصلی صفحات داخلی (فقط یک فعال)
# ============================================================
class MainBanner(models.Model):

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    order = models.PositiveIntegerField(default=0, verbose_name="اولویت نمایش")

    slug = models.SlugField(unique=True, blank=True, verbose_name="اسلاگ")

    image = models.ImageField(
        upload_to="banner/image/", verbose_name="تصویر بنر"
    )

    # ---------- فارسی ----------
    title_p1_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان اول (فارسی)"
    )
    title_p2_fa = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان دوم (فارسی)"
    )
    subtitle_fa = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="زیرعنوان (فارسی)"
    )

    # ---------- انگلیسی ----------
    title_p1_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان اول (انگلیسی)"
    )
    title_p2_en = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="عنوان دوم (انگلیسی)"
    )
    subtitle_en = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="زیرعنوان (انگلیسی)"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="draft", verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "بنر داخلی"
        verbose_name_plural = "بنر داخلی"
        ordering = ("order", "-created_at")

    def clean(self):
        if self.status == "published":
            qs = MainBanner.objects.filter(status="published")
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("فقط یک بنر اصلی صفحات داخلی می‌تواند فعال باشد.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.title_p1_en or "main-banner"
            self.slug = slugify(base)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_p1_fa or f"بنر داخلی اصلی #{self.pk}"
