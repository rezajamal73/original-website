# app_auction/templatetags/auction_tags.py
from django import template
from app_auction.models import AuctionCategory, AuctionTag, Auction
from django.db.models import Q

register = template.Library()


# ------------------------------------
#   دسته‌بندی مزایده‌ها
# ------------------------------------
@register.inclusion_tag("RTL/auction/including/category_fa.html")
def auction_categories():
    """
    نمایش دسته‌بندی‌های مزایده همراه با تعداد مزایده‌های هر دسته.
    فقط دسته‌هایی نمایش داده می‌شوند که حداقل یک مزایده فعال داشته باشند.
    """
    categories = AuctionCategory.objects.all()
    categories_dict = {}

    for cat in categories:
        count = Auction.objects.filter(category=cat).count()
        if count > 0:
            categories_dict[cat.title_fa] = {
                "count": count,
                "slug": cat.slug,
            }

    return {"categories": categories_dict}


# ------------------------------------
#   آخرین مزایده‌ها
# ------------------------------------
@register.inclusion_tag("RTL/auction/including/recent_fa.html")
def auction_recent():
    auctions = (
        Auction.objects.filter(
            Q(status="ongoing") | Q(status="extended")
        )

        .order_by("-start_date_fa")[:10]
    )
    return {"auctions": auctions}

# ------------------------------------
#   برچسب‌های مزایده
# ------------------------------------
@register.inclusion_tag("RTL/auction/including/tags.html")
def auction_tags():
    """
    فقط تگ‌هایی را نمایش بده که حداقل یک مزایده داشته باشند
    """
    tags = []

    for tag in AuctionTag.objects.all():
        if Auction.objects.filter(tags=tag).exists():
            tags.append(tag)

    return {"tags": tags}