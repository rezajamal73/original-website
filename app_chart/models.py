from django.db import models
from django.utils.html import format_html


class Person(models.Model):
    name_fa = models.CharField("نام و نام خانوادگی (فارسی)", max_length=200)
    name_en = models.CharField("نام و نام خانوادگی (انگلیسی)", max_length=200, blank=True)

    # Position / Title
    position_fa = models.CharField("سمت (فارسی)", max_length=200)
    position_en = models.CharField("سمت (انگلیسی)", max_length=200, blank=True)

    # Photo
    photo = models.ImageField("عکس", upload_to="org_photos/")

    # Hierarchy
    parent = models.ForeignKey(
        "self",
        verbose_name="والد / سرپرست",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    order = models.PositiveIntegerField("ترتیب در زیرمجموعه", default=0)

    # Contact (optional)
    phone = models.CharField("تلفن", max_length=64, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    content_en = models.TextField(blank=True, verbose_name="متن انگلیسی")
    content_fa = models.TextField(blank=True, verbose_name="متن فارسی")

    # helper flags
    is_ceo = models.BooleanField("مدیرعامل", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "چارت سازمانی"
        verbose_name_plural = "چارت سازمانی کلی"
        ordering = ["parent__id", "order", "name_fa"]

    def __str__(self):
        return f"{self.name_fa} — {self.position_fa}"

    def photo_tag(self):
        if self.photo:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;" />',
                               self.photo.url)
        return "(No photo)"

    photo_tag.short_description = "عکس"
    photo_tag.allow_tags = True


class BoardMember(models.Model):
    name_fa = models.CharField("نام و نام خانوادگی (فارسی)", max_length=200)
    name_en = models.CharField("نام و نام خانوادگی (انگلیسی)", max_length=200, blank=True)

    # Position / Title
    position_fa = models.CharField("سمت (فارسی)", max_length=200)
    position_en = models.CharField("سمت (انگلیسی)", max_length=200, blank=True)

    # Photo
    photo = models.ImageField("عکس", upload_to="org_photos/")

    # Hierarchy
    parent = models.ForeignKey(
        "self",
        verbose_name="والد / سرپرست",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    order = models.PositiveIntegerField("ترتیب در زیرمجموعه", default=0)

    # Contact (optional)
    phone = models.CharField("تلفن", max_length=64, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    content_en = models.TextField(blank=True, verbose_name="متن انگلیسی")
    content_fa = models.TextField(blank=True, verbose_name="متن فارسی")

    # helper flags
    is_ceo = models.BooleanField("رئیس هیأت‌مدیره", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عضو هیأت‌مدیره"
        verbose_name_plural = "اعضای هیأت‌مدیره"
        ordering = ["parent__id", "order", "name_fa"]

    def __str__(self):
        return f"{self.name_fa} — {self.position_fa}"

    def photo_tag(self):
        if self.photo:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;" />',
                               self.photo.url)
        return "(No photo)"

    photo_tag.short_description = "عکس"
    photo_tag.allow_tags = True
