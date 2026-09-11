from django import template
from django.db.models import Count, Q

from app_product.models import ProductCategory, ProductTag, ProductCategory2

register = template.Library()


# =====================================================
# CATEGORY LIST (PERSIAN)
# =====================================================
@register.inclusion_tag('RTL/product/including/category_fa.html')
def product_category_list():
    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    return {"cat_list": categories}


# =====================================================
# CATEGORY LIST (ENGLISH)
# =====================================================
@register.inclusion_tag('LTR/product/including/category_en.html')
def product_category_list_en():
    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_en")
    )

    return {"cat_list": categories}


# =====================================================
# CATEGORY 2 LIST (PERSIAN)
# =====================================================
@register.inclusion_tag('RTL/product/including/category_2_fa.html')
def product_category_list_2():
    categories = (
        ProductCategory2.objects
        .annotate(
            product_count=Count(
                "products2",
                filter=Q(products2__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    return {"cat_list": categories}


# =====================================================
# CATEGORY 2 LIST (ENGLISH)
# =====================================================
@register.inclusion_tag('LTR/product/including/category_2_en.html')
def product_category_list_2_en():
    categories = (
        ProductCategory2.objects
        .annotate(
            product_count=Count(
                "products2",
                filter=Q(products2__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_en")
    )

    return {"cat_list": categories}


# =====================================================
# TAG LIST (PERSIAN)
# =====================================================
@register.inclusion_tag(
    'RTL/product/including/tags.html',
    takes_context=True
)
def product_tags(context):
    tags = (
        ProductTag.objects
        .annotate(
            product_count=Count(
                "product",
                filter=Q(product__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    return {
        "tags": tags,
        "request": context.get("request"),
    }


# =====================================================
# TAG LIST (ENGLISH)
# =====================================================
@register.inclusion_tag(
    'LTR/product/including/tags.html',
    takes_context=True
)
def product_tags_en(context):
    tags = (
        ProductTag.objects
        .annotate(
            product_count=Count(
                "product",
                filter=Q(product__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_en")
    )

    return {
        "tags": tags,
        "request": context.get("request"),
    }