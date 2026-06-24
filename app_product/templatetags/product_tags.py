from django import template
from django.db.models import Count, Q

from app_product.models import ProductCategory, ProductTag,ProductCategory2

register = template.Library()


# =====================================================
# CATEGORY LIST (ORDERED BY PRIORITY)
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
        .filter(product_count__gt=0)  # ⭐⭐⭐ این خط کلیدی است
        .order_by("priority", "title_fa")   # ⭐⭐⭐ حیاتی
    )

    return {"cat_list": categories}


@register.inclusion_tag('RTL/product/including/category_2_fa.html')
def product_category_list_2():
    categories = (
        ProductCategory2.objects  # تغییر به ProductCategory2 برای دسته‌بندی دوم
        .annotate(
            product_count=Count(
                "products2",  # اصلاح به "products2"
                filter=Q(products2__status="published")  # اصلاح به "products2"
            )
        )
        .filter(product_count__gt=0)  # ⭐⭐⭐ این خط کلیدی است
        .order_by("priority", "title_fa")  # ترتیب نمایش دسته‌بندی‌ها
    )

    return {"cat_list": categories}


# =====================================================
# TAG LIST (ORDERED BY PRIORITY)
# =====================================================
@register.inclusion_tag('RTL/product/including/tags.html', takes_context=True)
def product_tags(context):
    tags = (
        ProductTag.objects
        .annotate(
            product_count=Count(
                "product",
                filter=Q(product__status="published")
            )
        )
        .filter(product_count__gt=0)  # ⭐⭐⭐ این خط کلیدی است
        .order_by("priority", "title_fa")   # ⭐⭐⭐ حیاتی
    )

    return {
        "tags": tags,
        "request": context.get("request"),
    }
