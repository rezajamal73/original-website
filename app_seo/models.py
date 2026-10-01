# app_seo/models.py

from django.db import models
from django.utils import timezone


# =====================================================
#  SEOSetting  —  هسته اصلی (سازگار با داده‌های فعلی)
# =====================================================

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

    # -------------------------------------------------
    # Yoast — وضعیت و امتیاز
    # -------------------------------------------------

    ROBOTS_INDEX_CHOICES = (
        ("index", "Index"),
        ("noindex", "No Index"),
    )

    ROBOTS_FOLLOW_CHOICES = (
        ("follow", "Follow"),
        ("nofollow", "No Follow"),
    )

    TWITTER_CARD_CHOICES = (
        ("summary", "Summary"),
        ("summary_large_image", "Summary Large Image"),
    )

    SCHEMA_TYPE_CHOICES = (
        ("auto", "🤖 خودکار"),
        ("Organization", "Organization"),
        ("WebSite", "WebSite"),
        ("WebPage", "WebPage"),
        ("AboutPage", "AboutPage"),
        ("ContactPage", "ContactPage"),
        ("Product", "Product"),
        ("Article", "Article"),
        ("NewsArticle", "NewsArticle"),
        ("BreadcrumbList", "BreadcrumbList"),
        ("FAQPage", "FAQPage"),
        ("Person", "Person"),
        ("CreativeWork", "CreativeWork"),
        ("CollectionPage", "CollectionPage"),
    )

    PUBLISH_STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
        ("scheduled", "زمان‌بندی شده"),
        ("expired", "منقضی شده"),
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
    # Yoast — Focus Keyphrase & Score
    # =====================

    focus_keyphrase = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="عبارت کلیدی اصلی",
        help_text="عبارتی که می‌خواهید این صفحه برای آن رتبه بگیرد (Yoast Focus Keyphrase)."
    )

    seo_score = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="امتیاز SEO",
        help_text="امتیاز ۰ تا ۱۰۰ که توسط تحلیل‌گر Yoast محاسبه می‌شود."
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

    # -------------------------------------------------
    # Robots  —  حفظ فیلد قدیمی برای سازگاری
    # -------------------------------------------------

    robots = models.CharField(
        max_length=100,
        default="index,follow",
        verbose_name="Robots (سازگاری)",
        help_text="مقدار کامل robots. برای کنترل دقیق‌تر از فیلدهای Index و Follow استفاده کنید."
    )

    # -------------------------------------------------
    # Robots  —  کنترل دقیق Yoast-style
    # -------------------------------------------------

    index_control = models.CharField(
        max_length=10,
        choices=ROBOTS_INDEX_CHOICES,
        default="index",
        verbose_name="Index",
    )

    follow_control = models.CharField(
        max_length=10,
        choices=ROBOTS_FOLLOW_CHOICES,
        default="follow",
        verbose_name="Follow",
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
    # Twitter Card
    # =====================

    twitter_card = models.CharField(
        max_length=30,
        choices=TWITTER_CARD_CHOICES,
        default="summary_large_image",
        verbose_name="نوع Twitter Card",
    )

    twitter_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="عنوان توییتر",
    )

    twitter_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="توضیحات توییتر",
    )

    twitter_image = models.ImageField(
        upload_to="seo/twitter/",
        blank=True,
        null=True,
        verbose_name="تصویر توییتر",
    )

    # =====================
    # Schema
    # =====================

    schema_type = models.CharField(
        max_length=40,
        choices=SCHEMA_TYPE_CHOICES,
        default="auto",
        verbose_name="نوع Schema",
        help_text="در حالت خودکار، بر اساس نوع محتوا انتخاب می‌شود."
    )

    schema_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Schema JSON-LD",
        help_text="اطلاعات ساختاریافته برای گوگل مانند محصول، مقاله، سازمان و..."
    )

    # =====================
    # Breadcrumb
    # =====================

    breadcrumb_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="عنوان Breadcrumb",
        help_text="در صورت خالی بودن، از عنوان SEO استفاده می‌شود."
    )

    # =====================
    # Hreflang
    # =====================

    hreflang_group = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="گروه Hreflang",
        help_text="شناسه مشترک برای صفحات زبان‌های مختلف یک محتوا."
    )

    # =====================
    # زمان‌بندی و وضعیت انتشار
    # =====================

    publish_status = models.CharField(
        max_length=20,
        choices=PUBLISH_STATUS_CHOICES,
        default="published",
        verbose_name="وضعیت انتشار",
    )

    publish_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="زمان انتشار",
    )

    expire_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="زمان انقضا",
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

            models.Index(
                fields=[
                    "focus_keyphrase",
                ]
            ),

            models.Index(
                fields=[
                    "hreflang_group",
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


    # =====================
    # خروجی‌های محاسباتی
    # =====================

    @property
    def effective_robots(self):
        """
        مقدار نهایی robots بر اساس index_control و follow_control.
        برای سازگاری با تمپلیت‌هایی که seo.robots را می‌خوانند.
        """
        return f"{self.index_control},{self.follow_control}"


    @property
    def effective_og_title(self):
        return self.og_title or self.title


    @property
    def effective_og_description(self):
        return self.og_description or self.description


    @property
    def effective_twitter_title(self):
        return self.twitter_title or self.effective_og_title


    @property
    def effective_twitter_description(self):
        return self.twitter_description or self.effective_og_description


    @property
    def effective_breadcrumb_title(self):
        return self.breadcrumb_title or self.title


    def is_published_now(self):
        now = timezone.now()

        if self.publish_status != "published":
            return False

        if self.publish_at and self.publish_at > now:
            return False

        if self.expire_at and self.expire_at < now:
            return False

        return True


    def __str__(self):

        if self.page_key:
            return f"📄 {self.page_key}"


        if self.object_id:
            return f"{self.model_name} - {self.object_id}"


        return self.title


# =====================================================
#  SEODefault  —  تنظیمات پیش‌فرض برای هر نوع محتوا و زبان
# =====================================================

class SEODefault(models.Model):

    LANGUAGE_CHOICES = (
        ("fa", "فارسی"),
        ("en", "English"),
    )

    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="fa",
        verbose_name="زبان",
    )

    content_type = models.CharField(
        max_length=30,
        choices=SEOSetting.CONTENT_TYPES,
        verbose_name="نوع محتوا",
    )

    title_template = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="الگوی عنوان",
        help_text="می‌توانید از {title} و {site} استفاده کنید."
    )

    description_template = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="الگوی توضیحات",
        help_text="می‌توانید از {title} و {site} استفاده کنید."
    )

    default_og_image = models.ImageField(
        upload_to="seo/defaults/",
        blank=True,
        null=True,
        verbose_name="تصویر پیش‌فرض OG",
    )

    default_schema_type = models.CharField(
        max_length=40,
        choices=SEOSetting.SCHEMA_TYPE_CHOICES,
        default="auto",
        verbose_name="نوع Schema پیش‌فرض",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "🧩 پیش‌فرض SEO"

        verbose_name_plural = "🧩 پیش‌فرض‌های SEO"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "language",
                    "content_type",
                ],
                name="unique_seo_default_per_language",
            ),

        ]

    def __str__(self):
        return f"{self.get_language_display()} - {self.get_content_type_display()}"


# =====================================================
#  SEOAnalysisLog  —  لاگ تحلیل Yoast (اختیاری)
# =====================================================

class SEOAnalysisLog(models.Model):

    seo_setting = models.ForeignKey(
        SEOSetting,
        on_delete=models.CASCADE,
        related_name="analysis_logs",
        verbose_name="تنظیم SEO",
    )

    score = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="امتیاز",
    )

    checks = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="جزئیات بررسی‌ها",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ تحلیل",
    )

    class Meta:

        verbose_name = "📊 لاگ تحلیل SEO"

        verbose_name_plural = "📊 لاگ‌های تحلیل SEO"

        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.seo_setting} - {self.score}/100"