from django import template
from app_tender.models import TenderCategory, TenderTag, Tender

from django.db.models import Q
register = template.Library()


# ------------------------------------
#   دسته‌بندی مناقصه‌ها
# ------------------------------------
@register.inclusion_tag("RTL/tender/including/category_fa.html")
def tender_categories():
    categories = TenderCategory.objects.all()
    categories_dict = {}

    for cat in categories:
        count = Tender.objects.filter(category=cat).count()
        if count > 0:
            categories_dict[cat.title_fa] = {
                "count": count,
                "slug": cat.slug,
            }

    return {"categories": categories_dict}


# ------------------------------------
#   آخرین مناقصه‌ها
# ------------------------------------
@register.inclusion_tag("RTL/tender/including/recent_fa.html")
def tender_recent():
    tenders = Tender.objects.filter(
            Q(status="ongoing") | Q(status="extended")
        ).order_by("-start_date_fa")[:10]
    return {"tenders": tenders}


# ------------------------------------
#   برچسب‌ها
# ------------------------------------
@register.inclusion_tag("RTL/tender/including/tags.html")
def tender_tags():
    """
    فقط تگ‌هایی را نمایش می‌دهد که حداقل یک مناقصه (Tender) به آن تگ مرتبط باشد.
    """
    tags = []

    for tag in TenderTag.objects.all():
        if Tender.objects.filter(tags=tag).exists():
            tags.append(tag)

    return {"tags": tags}
