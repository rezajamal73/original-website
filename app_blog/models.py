from django.db import models
from django.utils.text import slugify
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
from django.urls import reverse

# -------------------------------------------------------
#   تابع تولید اسلاگ یکتا
# -------------------------------------------------------
def unique_slugify(instance, value, slug_field_name='slug'):
    base_slug = slugify(value) or "item"
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
    slug = models.SlugField(unique=True, blank=True)

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ("-created_at_fa","order")

    def save(self, *args, **kwargs):
        if not self.slug:
            title_value = self.title_en or self.title_fa
            self.slug = unique_slugify(self, title_value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# -------------------------------------------------------
#   TAG (Sortable)
# -------------------------------------------------------
class blog_Tag(TimeStampedModel):
    title_fa = models.CharField(max_length=255, verbose_name="عنوان فارسی")
    title_en = models.CharField(max_length=255, verbose_name="عنوان انگلیسی")
    slug = models.SlugField(unique=True, blank=True)

    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ("-created_at_fa","order")

    def save(self, *args, **kwargs):
        if not self.slug:
            title_value = self.title_en or self.title_fa
            self.slug = unique_slugify(self, title_value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa


# -------------------------------------------------------
#   BLOG (Already sortable)
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
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='blog/image', default='blog/default.jpg', verbose_name="عکس اصلی")
    upload_file = models.FileField(upload_to='blog/upload_file', null=True, blank=True, verbose_name="آپلود فایل")
    category = models.ForeignKey(blog_Category, on_delete=models.CASCADE, related_name="blog", verbose_name="دسته‌بندی")
    tags = models.ManyToManyField(blog_Tag, related_name="blog", blank=True, verbose_name="برچسب‌ها")
    content_1_fa = models.TextField(verbose_name="متن فارسی 1")
    content_1_en = models.TextField(verbose_name="متن انگلیسی 1")
    content_2_fa = models.TextField(blank=True,verbose_name="متن فارسی 2")
    content_2_en = models.TextField(blank=True,verbose_name="متن انگلیسی 2")

    publish_date_fa = jmodels.jDateField(verbose_name="تاریخ انتشار (شمسی)", help_text="1373-08-10")
    publish_date_en = models.DateField(verbose_name="تاریخ انتشار (میلادی)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="وضعیت")
    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["order", "-publish_date_fa",]

    def save(self, *args, **kwargs):
        if not self.slug:
            title_value = self.title_en or self.title_fa
            self.slug = unique_slugify(self, title_value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_fa

    def get_absolute_url(self):
        return reverse("app_blog:blog_single", kwargs={"pid": self.id})

# -------------------------------------------------------
#   BLOG IMAGE
# -------------------------------------------------------
class BlogImage(models.Model):
    blog = models.ForeignKey(blog, on_delete=models.CASCADE, related_name="images", verbose_name="مقاله")
    image = models.ImageField(upload_to="blog/gallery/", verbose_name="تصویر")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر مقاله"
        verbose_name_plural = "گالری"
        ordering = ["order", "id"]

    def __str__(self):
        return f"تصویر {self.blog.title_fa} - ترتیب {self.order}"



