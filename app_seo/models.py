from django.db import models


class SEOSetting(models.Model):

    CONTENT_TYPES = (

        ("page", "📄 صفحه ثابت"),
        ("product", "📦 محصول"),
        ("blog", "📝 مقاله"),
        ("news", "📰 خبر"),
        ("media", "🎥 رسانه"),
        ("tender", "📑 مناقصه"),
        ("holding", "🏢 شرکت هلدینگ"),
        ("auction", "🏛 مزایده"),
        ("catalog", "📚 کاتالوگ"),
        ("resume", "💼 رزومه"),
        ("hr", "👨‍💼 فرصت شغلی"),
        ("chart", "📊 چارت سازمانی"),
        ("other", "🔹 سایر"),

    )


    # نوع محتوا
    content_type = models.CharField(
        max_length=30,
        choices=CONTENT_TYPES,
        default="page",
        verbose_name="نوع محتوا"
    )


    # برای صفحات ثابت
    page_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="کلید صفحه"
    )


    # اتصال به مدل‌ها
    app_label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نام اپلیکیشن"
    )


    model_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نام مدل"
    )


    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="شناسه محتوا"
    )


    # URL دستی
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name="آدرس صفحه"
    )


    # =====================
    # META SEO
    # =====================

    title = models.CharField(
        max_length=70,
        verbose_name="عنوان SEO"
    )


    description = models.CharField(
        max_length=160,
        verbose_name="توضیحات SEO"
    )


    keywords = models.TextField(
        blank=True,
        verbose_name="کلمات کلیدی"
    )


    canonical = models.URLField(
        blank=True,
        verbose_name="Canonical"
    )


    robots = models.CharField(
        max_length=100,
        default="index,follow",
        verbose_name="Robots"
    )


    # =====================
    # Open Graph
    # =====================

    og_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="OG Title"
    )


    og_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="OG Description"
    )


    og_image = models.ImageField(
        upload_to="seo/og/",
        blank=True,
        null=True,
        verbose_name="OG Image"
    )


    og_type = models.CharField(
        max_length=30,
        default="website",
        verbose_name="OG Type"
    )


    # =====================
    # Twitter
    # =====================

    twitter_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Twitter Title"
    )


    twitter_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Twitter Description"
    )


    twitter_image = models.ImageField(
        upload_to="seo/twitter/",
        blank=True,
        null=True,
        verbose_name="Twitter Image"
    )


    twitter_card = models.CharField(
        max_length=50,
        default="summary_large_image",
        verbose_name="Twitter Card"
    )


    # =====================
    # Schema
    # =====================

    schema_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Schema JSON-LD"
    )


    # =====================
    # وضعیت
    # =====================

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )


    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )


    class Meta:

        verbose_name = "⚙️ تنظیم SEO"
        verbose_name_plural = "⚙️ تنظیمات SEO"


        indexes = [

            models.Index(
                fields=[
                    "content_type",
                    "page_key",
                ]
            ),

            models.Index(
                fields=[
                    "app_label",
                    "model_name",
                    "object_id",
                ]
            ),

        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "app_label",
                    "model_name",
                    "object_id",
                ],
                condition=models.Q(
                    object_id__isnull=False
                ),
                name="unique_seo_object",
            ),

            models.UniqueConstraint(
                fields=[
                    "page_key",
                ],
                condition=models.Q(
                    content_type="page"
                ),
                name="unique_seo_page",
            ),

        ]


    def __str__(self):

        if self.page_key:
            return f"📄 {self.page_key}"

        if self.object_id:
            return f"{self.model_name} - {self.object_id}"

        return self.title