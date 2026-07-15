from django.db import models
from urllib.parse import urlparse
from django.utils.safestring import mark_safe
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


# =====================================================
# CORPORATE SECTION
# =====================================================
class CorporateSection(models.Model):
    """
    بخش‌های اصلی محتوای شرکتی سایت
    """

    SECTION_CHOICES = (
        ("about", "درباره ما"),
        ("history", "تاریخچه شرکت"),
        ("financial", "اطلاعیه‌ها و گزارشات مالی"),
        ("shareholder", "امور سهام"),
        ("governance", " اعضاء کمیته ها"),
        ("vision", "چشم‌انداز و مأموریت‌ها"),
        ("sustainability", "گزارش‌های حاکمیت شرکت"),
        ("certificate", "گواهینامه‌ها و استانداردها"),
    )

    section_type = models.CharField(
        max_length=30,
        choices=SECTION_CHOICES,
        unique=True,
        verbose_name="نوع بخش",
        help_text="هر نوع بخش فقط یک‌بار قابل تعریف است"
    )

    is_published = models.BooleanField(
        default=True,
        verbose_name="وضعیت انتشار",
        help_text="در صورت غیرفعال بودن، این بخش در سایت نمایش داده نمی‌شود"
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
        verbose_name = "بخش محتوای شرکتی"
        verbose_name_plural = "بخش‌های محتوای شرکتی"

    def __str__(self):
        return self.get_section_type_display()


# =====================================================
# CORPORATE TEXT
# =====================================================
class CorporateText(models.Model):
    """
    بلاک‌های متنی هر بخش (فارسی و انگلیسی)
    """

    section = models.ForeignKey(
        CorporateSection,
        on_delete=models.CASCADE,
        related_name="texts",
        verbose_name="بخش مربوطه"
    )

    title_fa = models.CharField(
        max_length=255,
        verbose_name="عنوان فارسی",
        help_text="عنوانی که در نسخه فارسی سایت نمایش داده می‌شود"
    )

    title_en = models.CharField(
        max_length=255,
        verbose_name="عنوان انگلیسی",
        help_text="عنوان این بخش در نسخه انگلیسی سایت"
    )

    content_fa = models.TextField(
        verbose_name="متن فارسی",
        help_text="محتوای کامل فارسی این بخش"
    )

    content_en = models.TextField(
        verbose_name="متن انگلیسی",
        help_text="محتوای کامل انگلیسی این بخش"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
        help_text="عدد کوچکتر زودتر نمایش داده می‌شود"
    )

    class Meta:
        ordering = ["display_order"]
        verbose_name = "بلاک متنی"
        verbose_name_plural = "بلاک‌های متنی"

    def __str__(self):
        return self.title_fa or self.title_en or "بلاک متنی بدون عنوان"


# =====================================================
# CORPORATE ATTACHMENT
# =====================================================
class CorporateAttachment(models.Model):
    """
    فایل‌ها و پیوست‌های مرتبط با بلاک متنی
    """

    text = models.ForeignKey(
        CorporateText,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="بلاک متنی مربوطه"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان فایل",
        help_text="عنوانی که کاربر در سایت مشاهده می‌کند"
    )

    file = models.FileField(
        upload_to="corporate/attachments/",
        verbose_name="فایل پیوست"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    class Meta:
        ordering = ["display_order"]
        verbose_name = "پیوست"
        verbose_name_plural = "پیوست‌ها"

    def __str__(self):
        return self.title


# =====================================================
# CORPORATE STATISTIC
# =====================================================
class CorporateStatistic(models.Model):
    """
    آمارها و شمارنده‌های عددی سایت
    """

    title_fa = models.CharField(
        max_length=255,
        verbose_name="عنوان آمار فارسی",
        help_text="مثال: تعداد محصولات، تعداد کشورها و ..."
    )
    title_en = models.CharField(
        max_length=255,
        verbose_name="عنوان آمار انگلیسی",
        help_text="مثال: تعداد محصولات، تعداد کشورها و ..."
    )

    value = models.PositiveIntegerField(
        verbose_name="عدد"
    )

    suffix = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="پسوند",
        help_text="مانند: K ، + ، % (اختیاری)"
    )

    icon_svg = models.FileField(
        upload_to="corporate/icons/",
        blank=True,
        null=True,
        verbose_name="آیکن SVG",
        help_text="فایل SVG با پس‌زمینه شفاف"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال بودن"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        ordering = ["display_order"]
        verbose_name = "آمار عددی"
        verbose_name_plural = "آمارهای عددی"

    def __str__(self):
        return f"{self.title_fa} ({self.value}{self.suffix})"


# =====================================================
# ABOUT YEAR
# =====================================================
class AboutYear(models.Model):
    """
    سابقه تأسیس (فقط یک مورد مجاز)
    """

    section = models.OneToOneField(
        CorporateSection,
        on_delete=models.CASCADE,
        related_name="about_year",
        limit_choices_to={"section_type": "about"},
        verbose_name="بخش درباره ما"
    )

    year = models.PositiveIntegerField(
        verbose_name="سابقه تأسیس",
        help_text="مثال: 37"
    )

    class Meta:
        verbose_name = "سابقه تأسیس"
        verbose_name_plural = "سابقه تأسیس"

    def __str__(self):
        return str(self.year)

    def clean(self):
        if AboutYear.objects.exclude(pk=self.pk).exists():
            raise ValidationError("فقط یک سال تأسیس برای بخش درباره ما مجاز است.")


# =====================================================
# ABOUT ITEM
# =====================================================
class AboutItem(models.Model):
    """
    آیتم‌های متنی بخش درباره ما
    """

    section = models.ForeignKey(
        CorporateSection,
        on_delete=models.CASCADE,
        related_name="about_items",
        limit_choices_to={"section_type": "about"},
        verbose_name="بخش درباره ما"
    )

    title_fa = models.CharField(
        max_length=255,
        verbose_name="عنوان آیتم فارسی"
    )
    title_en = models.CharField(
        max_length=255,
        verbose_name="عنوان آیتم انگلیسی"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = "آیتم درباره ما"
        verbose_name_plural = "آیتم‌های درباره ما"

    def __str__(self):
        return self.title_fa


# =====================================================
# GROUP COMPANY
# =====================================================
class GroupCompany(models.Model):
    """
    شرکت‌های هم‌گروه
    """

    name = models.CharField(
        max_length=255,
        verbose_name="نام شرکت"
    )

    logo = models.ImageField(
        upload_to="group_companies/logos/",
        verbose_name="لوگوی شرکت",
        help_text="ترجیحاً با پس‌زمینه شفاف"
    )

    website = models.URLField(
        blank=True,
        verbose_name="آدرس وب‌سایت",
        help_text="در صورت نیاز می‌توانید بدون https وارد کنید"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = "شرکت هم‌گروه"
        verbose_name_plural = "شرکت‌های هم‌گروه"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.website:
            url = self.website.strip()
            parsed = urlparse(url)
            if not parsed.scheme:
                url = "https://" + url
            self.website = url.rstrip("/")
        super().save(*args, **kwargs)


# =====================================================
# SITE MAIN INFO
# =====================================================
class SiteMainInfo(models.Model):
    """
    اطلاعات اصلی و عمومی سایت
    فقط یک رکورد مجاز است
    """
    designer_name_fa = models.CharField(max_length=255, blank=True, null=True, verbose_name=" طراحی شده توسط (فارسی)")
    designer_name_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="طراحی شده توسط (انگلیسی)")
    name_company_p1_fa = models.CharField(verbose_name="نام شرکت فارسی قسمت اول")
    name_company_p2_fa = models.CharField(verbose_name="نام شرکت فارسی قسمت دوم")
    name_company_p1_en = models.CharField(blank=True, null=True, verbose_name="نام شرکت انگلیسی قسمت اول")
    name_company_p2_en = models.CharField(blank=True, null=True, verbose_name="نام شرکت انگلیسی قسمت دوم")
    slogan_fa = models.CharField(max_length=255, blank=True, null=True, verbose_name="شعار شرکت (فارسی)")
    slogan_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="شعار شرکت (انگلیسی)")

    header_logo = models.ImageField(blank=True, null=True, upload_to="site/logos/", verbose_name="لوگوی هدر")
    footer_logo = models.ImageField(blank=True, null=True, upload_to="site/logos/", verbose_name="لوگوی فوتر")
    sidebar_logo = models.ImageField(blank=True, null=True, upload_to="site/logos/", verbose_name="لوگوی سایدبار")

    phone_1 = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره تماس 1")
    phone_2 = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره تماس 2")
    phone_3 = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس 3")
    phone_4 = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس 4")
    phone_5 = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس 5")

    phone_security_1 = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره تماس 1")
    phone_security_2 = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره تماس 2")
    phone_security_3 = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره تماس 3")
    email_security = models.EmailField(blank=True, null=True, verbose_name="ایمیل رسمی حراست")
    fax_security = models.CharField(blank=True, null=True, max_length=20, verbose_name="فکس")

    suport_phone = models.CharField(blank=True, null=True, max_length=20, verbose_name="شماره پشتیبانی")

    fax_1 = models.CharField(blank=True, null=True, max_length=20, verbose_name="فکس 1")
    fax_2 = models.CharField(blank=True, null=True, max_length=20, verbose_name="فکس 2")
    fax_3 = models.CharField(blank=True, null=True, max_length=20, verbose_name="فکس 3")

    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل رسمی")
    postal_code = models.CharField(blank=True, null=True, max_length=20, verbose_name="کد پستی")
    address_fa = models.TextField(blank=True, null=True, verbose_name="آدرس کامل فارسی")
    address_en = models.TextField(blank=True, null=True, verbose_name="آدرس کامل انگلیسی")

    work_days_fa = models.CharField(blank=True, null=True, max_length=255, verbose_name="روز کاری فارسی")
    work_days_en = models.CharField(blank=True, null=True, max_length=255, verbose_name="روز کاری انگلیسی")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ساختار سایت"
        verbose_name_plural = "اطلاعات اصلی سایت"

    def clean(self):
        if SiteMainInfo.objects.exclude(pk=self.pk).exists():
            raise ValidationError("فقط یک رکورد اطلاعات اصلی سایت مجاز است.")

    def __str__(self):
        return "اطلاعات اصلی سایت"


from django.db import models
from django.core.validators import URLValidator


# =====================================================
# لینک‌های «ما را دنبال کنید» (شبکه‌های اجتماعی)
# =====================================================
class FollowUsLink(models.Model):
    """
    لینک‌های شبکه‌های اجتماعی (ما را دنبال کنید)
    """

    title = models.CharField(
        max_length=50,
        verbose_name="نام شبکه اجتماعی",
        help_text="مثال: اینستاگرام، لینکدین، تلگرام"
    )

    url = models.URLField(
        validators=[URLValidator()],
        verbose_name="آدرس لینک",
        help_text="آدرس کامل صفحه شبکه اجتماعی"
    )

    svg_icon = models.FileField(
        upload_to="icons/social/",
        verbose_name="آیکن شبکه اجتماعی (SVG)",
        help_text="فقط فایل SVG آپلود شود"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال باشد؟"
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = "لینک شبکه اجتماعی"
        verbose_name_plural = "لینک‌های شبکه اجتماعی"

    def __str__(self):
        return self.title


class DepartmentContact(models.Model):
    department_name_fa = models.CharField(
        max_length=100,
        verbose_name="نام دپارتمان (فارسی)",
        help_text="مثال: فروش، پشتیبانی، منابع انسانی"
    )

    department_name_en = models.CharField(
        max_length=100,
        verbose_name="نام دپارتمان (انگلیسی)",
        help_text="Example: Sales, Support, Human Resources"
    )

    phone_1 = models.CharField(
        max_length=20,
        verbose_name="شماره تماس اصلی"
    )

    phone_2 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس جایگزین",
        help_text="در صورت وجود وارد شود"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل دپارتمان",
        help_text="example@company.com"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = "شماره تماس دپارتمان"
        verbose_name_plural = "شماره تماس دپارتمان‌ها"

    def __str__(self) -> str:
        return f"{self.department_name_fa} | {self.phone_1}"
