from django import template
from django.db.models import Q, Count
from app_tender_holding.models import Holding, HoldingCategory, HoldingTag

register = template.Library()

# ------------------------------------
#   دسته‌بندی هلدینگ‌ها
# ------------------------------------
@register.inclusion_tag("RTL/tender_holding/including/category_fa.html")
def holding_categories():
    """
    فقط دسته‌بندی‌هایی که حداقل یک هلدینگ دارند
    + شمارش هلدینگ‌ها
    """
    categories = (
        HoldingCategory.objects
        .annotate(holding_count=Count("holdings"))
        .filter(holding_count__gt=0)
        .order_by("order")
    )

    categories_dict = {
        cat.title_fa: {
            "count": cat.holding_count,  # تعداد هلدینگ‌ها
            "slug": cat.slug,
        }
        for cat in categories
    }

    return {"categories": categories_dict}


# ------------------------------------
#   هلدینگ‌های فعال (ongoing / extended)
# ------------------------------------
@register.inclusion_tag("RTL/tender_holding/including/recent_fa.html")
def holding_recent():
    holdings = (
        Holding.objects
        .filter(Q(status="ongoing") | Q(status="extended"))  # فیلتر وضعیت‌ها
        .order_by("-start_date_fa")[:10]
    )

    return {"tenders": holdings}  # اسم tenders نگه داشته شده برای سازگاری با template


# ------------------------------------
#   برچسب‌ها (فقط دارای هلدینگ)
# ------------------------------------
@register.inclusion_tag("RTL/tender_holding/including/tags.html")
def holding_tags():
    """
    فقط تگ‌هایی که حداقل یک هلدینگ دارند
    """
    tags = (
        HoldingTag.objects
        .filter(holdings__isnull=False)
        .distinct()
        .order_by("order")
    )

    return {"tags": tags}
