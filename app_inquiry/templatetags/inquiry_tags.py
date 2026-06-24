from django import template
from django.db.models import Q, Count

from app_inquiry.models import (
    InquiryCategory,
    InquiryTag,
    PurchaseInquiry,
)

register = template.Library()


# ------------------------------------
#   دسته‌بندی‌های استعلام خرید
# ------------------------------------
@register.inclusion_tag("RTL/inquiry/including/category_fa.html")
def inquiry_categories():
    """
    نمایش دسته‌بندی‌های استعلام خرید
    همراه با تعداد کل استعلام‌ها (بدون فیلتر وضعیت)
    فقط دسته‌هایی که حداقل یک استعلام دارند
    """
    categories = (
        InquiryCategory.objects
        .annotate(inquiry_count=Count("inquiries"))
        .filter(inquiry_count__gt=0)
        .order_by("order", "title_fa")
    )

    categories_dict = {
        cat.title_fa: {
            "count": cat.inquiry_count,
            "slug": cat.slug,
        }
        for cat in categories
    }

    return {"categories": categories_dict}


# ------------------------------------
#   آخرین استعلام‌های فعال
# ------------------------------------
@register.inclusion_tag("RTL/inquiry/including/recent_fa.html")
def inquiry_recent(limit=10):
    """
    نمایش آخرین استعلام‌های فعال (open + extended)
    """
    inquiries = (
        PurchaseInquiry.objects
        .filter(Q(status="open") | Q(status="extended"))
        .order_by("-start_date_fa")[:limit]
    )
    return {"inquiries": inquiries}


# ------------------------------------
#   برچسب‌های استعلام خرید
# ------------------------------------
@register.inclusion_tag("RTL/inquiry/including/tags.html")
def inquiry_tags():
    """
    فقط تگ‌هایی را نمایش بده که حداقل یک استعلام دارند
    """
    tags = (
        InquiryTag.objects
        .annotate(inquiry_count=Count("inquiries"))
        .filter(inquiry_count__gt=0)
        .order_by("order", "title_fa")
    )

    return {"tags": tags}
