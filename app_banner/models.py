import os
from functools import partial

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


# ---------------------------------------
#   DYNAMIC APP-BASED UPLOAD PATH
# ---------------------------------------
def app_upload_to(instance, filename, subfolder=""):
    """
    ساخت مسیر آپلود به صورت داینامیک بر اساس نام اپ مدل.
    نتیجه: <app_label>/<subfolder>/<filename>
    """
    app_label = instance._meta.app_label
    return f"{app_label}/{subfolder}/{filename}".replace("//", "/")


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

    MEDIA_TYPE_CHOICES = (
        ("image", "🖼️ تصویر"),
        ("video", "🎬 ویدیو / GIF"),
    )

    order = models.PositiveIntegerField(
        default=0, verbose_name="اولویت نمایش"
    )

    # ✅ مدت زمان نمایش اسلاید (ثانیه)
    duration = models.PositiveIntegerField(
        default=5,
        verbose_name="مدت زمان نمایش (ثانیه)",
        help_text="مدت زمانی که این اسلاید نمایش داده می‌شود. مثلاً 5 = ۵ ثانیه"
    )

    # ✅ نوع مدیا (فقط یکی از دو حالت)
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default="image",
        verbose_name="نوع مدیا",
        help_text="⚠️ فقط یکی از دو حالت را انتخاب کنید و فقط فیلد مربوط به آن را پر کنید."
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

    # ✅ media/<app_label>/hero/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="hero"),
        blank=True,
        null=True,
        verbose_name="تصویر بنر",
        help_text="فقط در صورتی که «تصویر» را به عنوان نوع مدیا انتخاب کرده‌اید."
    )

    # ✅ media/<app_label>/hero/videos/...
    video = models.FileField(
        upload_to=partial(app_upload_to, subfolder="hero/videos"),
        blank=True,
        null=True,
        verbose_name="ویدیو/GIF بنر",
        help_text="فقط در صورتی که «ویدیو / GIF» را انتخاب کرده‌اید. فرمت‌های مجاز: MP4, WebM, OGG, GIF"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="draft", verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "بنر های اصلی پوستر"
        verbose_name_plural = "بنر های اصلی پوستر"
        ordering = ("order",)

    def clean(self):
        """اعتبارسنجی بر اساس نوع مدیای انتخاب‌شده"""

        # ---------- اعتبارسنجی بر اساس media_type ----------
        if self.media_type == "image":
            if not self.image:
                raise ValidationError({
                    "image": "لطفاً تصویر بنر را آپلود کنید."
                })
            if self.video:
                raise ValidationError({
                    "video": "شما نوع «تصویر» را انتخاب کرده‌اید. لطفاً فیلد ویدیو را خالی کنید یا نوع مدیا را به «ویدیو / GIF» تغییر دهید."
                })

        elif self.media_type == "video":
            if not self.video:
                raise ValidationError({
                    "video": "لطفاً ویدیو یا GIF بنر را آپلود کنید."
                })
            if self.image:
                raise ValidationError({
                    "image": "شما نوع «ویدیو / GIF» را انتخاب کرده‌اید. لطفاً فیلد تصویر را خالی کنید یا نوع مدیا را به «تصویر» تغییر دهید."
                })

            # اعتبارسنجی فرمت ویدیو
            ext = os.path.splitext(self.video.name)[1].lower()
            allowed_extensions = ['.mp4', '.webm', '.ogg', '.gif']
            if ext not in allowed_extensions:
                raise ValidationError({
                    "video": f"فرمت ویدیو باید یکی از موارد زیر باشد: {', '.join(allowed_extensions)}"
                })

        # ---------- اعتبارسنجی مدت زمان ----------
        if self.duration < 1:
            raise ValidationError({
                "duration": "مدت زمان نمایش نمی‌تواند کمتر از ۱ ثانیه باشد."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_p1_en or self.label_en or "hero-banner")
            slug = base_slug
            counter = 1

            while HeroBanner.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def media_source_type(self):
        """نوع منبع مدیا برای template (image / gif / video)"""
        if self.media_type == "video" and self.video:
            ext = os.path.splitext(self.video.name)[1].lower()
            if ext == '.gif':
                return 'gif'
            return 'video'
        return 'image'

    @property
    def media_url(self):
        """آدرس مدیا بر اساس نوع انتخاب‌شده"""
        if self.media_type == "video" and self.video:
            return self.video.url
        if self.media_type == "image" and self.image:
            return self.image.url
        return None

    @property
    def duration_ms(self):
        """مدت زمان به میلی‌ثانیه (برای استفاده در JavaScript)"""
        return self.duration * 1000

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

    # ✅ media/<app_label>/other/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="other"),
        verbose_name="تصویر بنر"
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

    # ✅ media/<app_label>/special-products/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="special-products"),
        verbose_name="تصویر بنر"
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

    # ✅ media/<app_label>/main/...
    image = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="main"),
        verbose_name="تصویر بنر"
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


class AboutBanner(models.Model):
    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    # ✅ media/<app_label>/about/...
    image_1 = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="about"),
        verbose_name="تصویر اول"
    )

    image_2 = models.ImageField(
        upload_to=partial(app_upload_to, subfolder="about"),
        verbose_name="تصویر دوم"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت انتشار"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تصاویر درباره ما"
        verbose_name_plural = "تصاویر درباره ما"

    def clean(self):
        if self.status == "published":
            qs = AboutBanner.objects.filter(status="published")
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("فقط یک بنر درباره ما می‌تواند منتشر شده باشد.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "تصاویر درباره ما"