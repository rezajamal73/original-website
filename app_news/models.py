from django.db import models
from django.utils.text import slugify
from django_jalali.db import models as jmodels
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

    slug = models.SlugField(unique=True, blank=True, editable=False)   # 🔒 کاربر نمی‌تواند تغییر دهد

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته خبر"
        verbose_name_plural = "دسته‌های خبر"
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.slug) != slugify(self.title_en):
            self.slug = generate_unique_slug(self, "slug", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ------------------------------------------------------
#   TAG
# ------------------------------------------------------
class NewsTag(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")

    slug = models.SlugField(unique=True, blank=True, editable=False)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"

    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.slug) != slugify(self.title_en):
            self.slug = generate_unique_slug(self, "slug", self.title_en)

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

    slug = models.SlugField(unique=True, blank=True, editable=False)   # 🔒 کاربر نمی‌تواند تغییر دهد

    summary_fa = models.TextField(verbose_name="متن قسمت اول فارسی")
    summary_en = models.TextField(verbose_name="متن  قسمت اول انگلیسی")

    content_fa = models.TextField(blank=True,verbose_name="متن قسمت دوم فارسی")
    content_en = models.TextField(blank=True,verbose_name="متن قسمت دوم انگلیسی")

    image = models.ImageField(upload_to="news/cover/", verbose_name="کاور خبر")

    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, related_name="news", verbose_name="دسته‌بندی"
    )
    tags = models.ManyToManyField(NewsTag,related_name="news_tags", verbose_name="برچسب‌ها")

    publish_date_fa = jmodels.jDateField(verbose_name="تاریخ انتشار (شمسی)", help_text="1373-08-10")
    publish_date_en = models.DateField(verbose_name="تاریخ انتشار (میلادی)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="وضعیت")
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
        if not self.slug or slugify(self.slug) != slugify(self.title_en):
            self.slug = generate_unique_slug(self, "slug", self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# ------------------------------------------------------
#   NEWS IMAGE
# ------------------------------------------------------
class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="news/gallery/")
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
    video = models.FileField(upload_to="news/videos/")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح ویدیو")
    duration = models.CharField(max_length=10, blank=True, null=True, verbose_name="مدت زمان ویدیو")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویدیوی خبر"
        verbose_name_plural = "ویدیوهای خبر"
        ordering = ["order", "id"]

    def __str__(self):
        return f"ویدیو {self.news.title_fa} - ترتیب {self.order}"
