from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum


class SalesReport(models.Model):
    """
    Stores monthly and yearly sales reports (Gregorian & Jalali).
    """

    # =================================================
    # Gregorian (Miladi)
    # =================================================
    class GregorianMonth(models.IntegerChoices):
        JANUARY = 1, "January"
        FEBRUARY = 2, "February"
        MARCH = 3, "March"
        APRIL = 4, "April"
        MAY = 5, "May"
        JUNE = 6, "June"
        JULY = 7, "July"
        AUGUST = 8, "August"
        SEPTEMBER = 9, "September"
        OCTOBER = 10, "October"
        NOVEMBER = 11, "November"
        DECEMBER = 12, "December"

    gregorian_year = models.PositiveIntegerField(
        verbose_name="سال میلادی",
        validators=[MinValueValidator(2000)]
    )
    gregorian_month = models.PositiveSmallIntegerField(
        verbose_name="ماه میلادی",
        choices=GregorianMonth.choices,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    # =================================================
    # Jalali (Shamsi)
    # =================================================
    class JalaliMonth(models.IntegerChoices):
        FARVARDIN = 1, "فروردین"
        ORDIBEHESHT = 2, "اردیبهشت"
        KHORDAD = 3, "خرداد"
        TIR = 4, "تیر"
        MORDAD = 5, "مرداد"
        SHAHRIVAR = 6, "شهریور"
        MEHR = 7, "مهر"
        ABAN = 8, "آبان"
        AZAR = 9, "آذر"
        DEY = 10, "دی"
        BAHMAN = 11, "بهمن"
        ESFAND = 12, "اسفند"

    jalali_year = models.PositiveIntegerField(
        verbose_name="سال شمسی",
        validators=[MinValueValidator(1300)]
    )
    jalali_month = models.PositiveSmallIntegerField(
        verbose_name="ماه شمسی",
        choices=JalaliMonth.choices,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    # =================================================
    # Sales
    # =================================================
    total_sales = models.DecimalField(
        verbose_name="مبلغ کل فروش",
        max_digits=15,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        verbose_name = "گزارش فروش"
        verbose_name_plural = "گزارش‌های فروش"
        unique_together = (
            "gregorian_year",
            "gregorian_month",
            "jalali_year",
            "jalali_month",
        )
        ordering = ("jalali_year", "jalali_month")

    # =================================================
    # String
    # =================================================
    def __str__(self) -> str:
        return (
            f"فروش {self.jalali_month_name} {self.jalali_year} | "
            f"{self.total_sales:,} تومان"
        )

    # =================================================
    # Helpers (Display)
    # =================================================
    @property
    def jalali_month_name(self) -> str:
        return self.get_jalali_month_display()

    @property
    def gregorian_month_name(self) -> str:
        return self.get_gregorian_month_display()

    # =================================================
    # Business Logic – دسته‌بندی حرفه‌ای
    # =================================================
    @classmethod
    def yearly_total(cls, jalali_year: int):
        """
        مجموع فروش یک سال شمسی
        """
        return (
            cls.objects
            .filter(jalali_year=jalali_year)
            .aggregate(total=Sum("total_sales"))
            .get("total") or 0
        )

    @classmethod
    def monthly_totals(cls, jalali_year: int):
        """
        فروش ماه‌به‌ماه یک سال شمسی (مرتب‌شده)
        خروجی مناسب نمودار
        """
        return (
            cls.objects
            .filter(jalali_year=jalali_year)
            .values("jalali_month")
            .annotate(total=Sum("total_sales"))
            .order_by("jalali_month")
        )

    @classmethod
    def yearly_summary(cls):
        """
        خلاصه فروش سالانه (همه سال‌ها)
        """
        return (
            cls.objects
            .values("jalali_year")
            .annotate(total=Sum("total_sales"))
            .order_by("jalali_year")
        )
