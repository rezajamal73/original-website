from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import django_jalali.db.models as jmodels
import jdatetime


# ============================================================
#   BASE TIMESTAMP MODEL (FIXED ✅)
# ============================================================
class TimeStampedModel(models.Model):
    created_at_fa = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name=_("تاریخ ایجاد (شمسی)"),
    )
    created_at_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at (EN)"),
    )
    updated_at_en = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at (EN)"),
    )

    class Meta:
        abstract = True

    # ✅ فقط تاریخ + ساعت + دقیقه (بدون ثانیه)
    @property
    def created_at_fa_display(self):
        if not self.created_at_en:
            return "—"
        j_date = jdatetime.datetime.fromgregorian(
            datetime=self.created_at_en
        )
        return j_date.strftime("%Y/%m/%d %H:%M")


# -------------------------------------------------
# VALIDATORS
# -------------------------------------------------
def validate_pdf_file(value):
    max_size = getattr(settings, "MAX_RESUME_FILE_SIZE", 3 * 1024 * 1024)

    if value.size > max_size:
        raise ValidationError(_("حجم فایل بیش از حد مجاز است."))

    if not value.name.lower().endswith(".pdf"):
        raise ValidationError(_("فقط فایل PDF مجاز است."))


# ============================================================
# JOB OPPORTUNITY
# ============================================================
class JobOpportunity(TimeStampedModel):

    RECRUITMENT_OPEN = "open"
    RECRUITMENT_CLOSED = "closed"

    RECRUITMENT_STATUS_CHOICES = (
        (RECRUITMENT_OPEN, _("در حال جذب نیرو")),
        (RECRUITMENT_CLOSED, _("اتمام جذب")),
    )

    # --------------------
    # MILITARY STATUS (FOR MALE)
    # --------------------
    MILITARY_STATUS_CHOICES = (
        ("completed", _("پایان خدمت")),
        ("exempt", _("بدون محدودیت درجذب")),
    )

    # --------------------
    # BASIC INFO
    # --------------------
    title = models.CharField(max_length=200, verbose_name=_("عنوان فراخوان"))
    position = models.CharField(max_length=200, verbose_name=_("عنوان شغلی"))
    activity = models.CharField(max_length=200, verbose_name=_("واحد / حوزه فعالیت"))

    # --------------------
    # CONDITIONS
    # --------------------
    min_age = models.PositiveSmallIntegerField(
        verbose_name=_("حداقل سن"),
    )

    max_age = models.PositiveSmallIntegerField(
        verbose_name=_("حداکثر سن"),
    )

    EDUCATION_CHOICES = (
        ("diploma", _("دیپلم")),
        ("associate", _("کاردانی")),
        ("bachelor", _("کارشناسی")),
        ("master", _("کارشناسی ارشد")),
        ("phd", _("دکتری")),
    )

    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        verbose_name=_("حداقل مدرک تحصیلی"),
    )

    GENDER_CHOICES = (
        ("male", _("مرد")),
        ("female", _("زن")),
        ("any", _("فرقی ندارد")),
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default="any",
        verbose_name=_("جنسیت"),
    )

    military_status_required = models.CharField(
        max_length=20,
        choices=MILITARY_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("وضعیت نظام وظیفه (ویژه آقایان)"),
    )

    min_experience_years = models.PositiveSmallIntegerField(
        verbose_name=_("حداقل سابقه کار (سال)"),
    )

    recruitment_status = models.CharField(
        max_length=10,
        choices=RECRUITMENT_STATUS_CHOICES,
        default=RECRUITMENT_OPEN,
        verbose_name=_("وضعیت جذب"),
    )

    # --------------------
    # CONTENT
    # --------------------
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name=_("اسلاگ"),
    )

    poster = models.ImageField(
        upload_to="job_posters/",
        verbose_name=_("پوستر فراخوان"),
    )

    description_1 = models.TextField(verbose_name=_("توضیحات فراخوان"))
    description_2 = models.TextField(verbose_name=_("مزایای شغلی"))

    start_date_fa = jmodels.jDateField(verbose_name=_("تاریخ (شمسی)"))

    start_date_en = models.DateField(
        editable=False,
        null=True,
        blank=True,
        verbose_name=_("تاریخ  (میلادی)"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ترتیب نمایش"),
    )

    class Meta:
        verbose_name = _("فراخوان جذب")
        verbose_name_plural = _("فراخوان‌های جذب")
        ordering = ("-created_at_fa","ordering")

    def clean(self):
        super().clean()
        if self.gender == "male" and not self.military_status_required:
            raise ValidationError({
                "military_status_required": _("برای آقایان، وضعیت نظام وظیفه الزامی است.")
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.position}", allow_unicode=True)
            slug = base_slug
            counter = 1
            while JobOpportunity.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.position}"


# ============================================================
# JOB APPLICATION
# ============================================================
class JobApplication(TimeStampedModel):

    STATUS_PENDING = "pending"
    STATUS_REVIEWED = "reviewed"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_REVIEWED, _("در حال بررسی")),
        (STATUS_ACCEPTED, _("پذیرفته شده")),
        (STATUS_REJECTED, _("رد شده")),
    )

    GENDER_CHOICES = (
        ("male", _("مرد")),
        ("female", _("زن")),
    )

    MARITAL_STATUS_CHOICES = (
        ("single", _("مجرد")),
        ("married", _("متأهل")),
    )

    MILITARY_STATUS_CHOICES = (
        ("completed", _("پایان خدمت")),
        ("exempt", _("معاف")),
    )

    EDUCATION_CHOICES = JobOpportunity.EDUCATION_CHOICES

    opportunity = models.ForeignKey(
        JobOpportunity,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("فراخوان"),
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        verbose_name=_("اسلاگ"),
    )

    first_name = models.CharField(max_length=100, verbose_name=_("نام"))
    last_name = models.CharField(max_length=100, verbose_name=_("نام خانوادگی"))

    national_code = models.CharField(max_length=10, verbose_name=_("کد ملی"))

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name=_("جنسیت"),
    )
    age = models.PositiveSmallIntegerField(
        verbose_name=_("سن"),
    )

    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
        verbose_name=_("وضعیت تأهل"),
    )

    military_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=MILITARY_STATUS_CHOICES,
        verbose_name=_("وضعیت نظام وظیفه"),
    )

    mobile = models.CharField(max_length=20, verbose_name=_("شماره تماس"))
    mobile_support = models.CharField(max_length=20, verbose_name=_("شماره تماس ضروری"))
    email = models.EmailField(verbose_name=_("پست الکترونیک"))

    resume_file = models.FileField(
        upload_to="resumes/",
        validators=[validate_pdf_file],
        verbose_name=_("رزومه"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_("وضعیت"),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("آی‌پی ارسال‌کننده"),
    )

    class Meta:
        verbose_name = _("درخواست جذب")
        verbose_name_plural = _("درخواست‌های جذب ارسال شده ")
        ordering = ("-created_at_en",)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                f"{self.full_name}-{self.opportunity_id}",
                allow_unicode=True
            )
            slug = base_slug
            counter = 1
            while JobApplication.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
