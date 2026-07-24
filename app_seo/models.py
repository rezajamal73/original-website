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


    # =====================
    # اتصال محتوا
    # =====================

    content_type = models.CharField(
        max_length=30,
        choices=CONTENT_TYPES,
        default="page",
        verbose_name="نوع محتوا",
        help_text="مشخص کنید این تنظیمات SEO برای چه نوع محتوایی است."
    )


    page_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="کلید صفحه",
        help_text="برای صفحات ثابت مانند درباره ما، تماس با ما و... یک شناسه یکتا وارد کنید."
    )


    app_label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نام اپلیکیشن",
        help_text="نام اپلیکیشن Django مربوط به محتوا (مثلاً app_product)."
    )


    model_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نام مدل",
        help_text="نام مدل Django مربوط به محتوا (مثلاً Product)."
    )


    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="شناسه محتوا",
        help_text="شناسه رکورد مربوط به محصول، مقاله، خبر یا سایر محتواها."
    )


    url = models.URLField(
        blank=True,
        null=True,
        verbose_name="آدرس صفحه",
        help_text="در صورت نیاز آدرس کامل صفحه را وارد کنید."
    )


    # =====================
    # META SEO
    # =====================

    title = models.CharField(
        max_length=70,
        verbose_name="عنوان SEO",
        help_text="عنوانی که در نتایج گوگل نمایش داده می‌شود. بهتر است کمتر از 70 کاراکتر باشد."
    )


    description = models.CharField(
        max_length=160,
        verbose_name="توضیحات SEO",
        help_text="توضیح کوتاه صفحه برای نمایش در موتورهای جستجو. بهتر است حدود 160 کاراکتر باشد."
    )


    keywords = models.TextField(
        blank=True,
        verbose_name="کلمات کلیدی",
        help_text="کلمات مرتبط با محتوا را با کاما جدا کنید."
    )


    canonical = models.URLField(
        blank=True,
        verbose_name="Canonical",
        help_text="آدرس اصلی صفحه برای جلوگیری از محتوای تکراری."
    )


    robots = models.CharField(
        max_length=100,
        default="index,follow",
        verbose_name="Robots",
        help_text="قوانین ایندکس شدن صفحه توسط موتورهای جستجو."
    )


    # =====================
    # Open Graph
    # =====================

    og_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="عنوان شبکه اجتماعی",
        help_text="عنوانی که هنگام اشتراک لینک در شبکه‌های اجتماعی نمایش داده می‌شود."
    )


    og_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="توضیحات شبکه اجتماعی",
        help_text="توضیح نمایش داده شده هنگام اشتراک لینک در شبکه‌های اجتماعی."
    )


    og_image = models.ImageField(
        upload_to="seo/og/",
        blank=True,
        null=True,
        verbose_name="تصویر شبکه اجتماعی",
        help_text="تصویری که هنگام اشتراک صفحه در شبکه‌های اجتماعی نمایش داده می‌شود."
    )


    og_type = models.CharField(
        max_length=30,
        default="website",
        verbose_name="نوع Open Graph",
        help_text="نوع محتوا برای شبکه‌های اجتماعی مانند website، article و..."
    )


    # =====================
    # Schema
    # =====================

    schema_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Schema JSON-LD",
        help_text="اطلاعات ساختاریافته برای گوگل مانند محصول، مقاله، سازمان و..."
    )


    # =====================
    # وضعیت
    # =====================

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="در صورت فعال بودن این تنظیمات SEO روی سایت اعمال می‌شود."
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