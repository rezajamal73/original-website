# app_blog/templatetags/blog_tags.py

from django import template
from django.db.models import Count, Q

from app_blog.models import blog, blog_Category, blog_Tag

register = template.Library()


# =====================================================
# BLOG CATEGORIES — PERSIAN
# =====================================================

@register.inclusion_tag("RTL/blog/including/category_fa.html")
def blog_category_fa():
    categories = (
        blog_Category.objects
        .annotate(
            count=Count(
                "blog",
                filter=Q(blog__status="published")
            )
        )
        .filter(count__gt=0)
        .order_by("order")
    )
    return {"categories": categories}


# =====================================================
# BLOG CATEGORIES — ENGLISH
# =====================================================

@register.inclusion_tag("LTR/blog/including/category_en.html")
def blog_category_en():
    categories = (
        blog_Category.objects
        .annotate(
            count=Count(
                "blog",
                filter=Q(blog__status="published")
            )
        )
        .filter(count__gt=0)
        .order_by("order")
    )
    return {"categories": categories}


# =====================================================
# RECENT BLOGS — PERSIAN
# =====================================================

@register.inclusion_tag("RTL/blog/including/recent_fa.html")
def blog_recent_fa():
    blogs = (
        blog.objects
        .filter(status="published")
        .order_by("-created_at_fa")[:3]
    )
    return {"blogs": blogs}


# =====================================================
# RECENT BLOGS — ENGLISH
# =====================================================

@register.inclusion_tag("LTR/blog/including/recent_en.html")
def blog_recent_en():
    blogs = (
        blog.objects
        .filter(status="published")
        .order_by("-created_at_fa")[:3]
    )
    return {"blogs": blogs}


# =====================================================
# BLOG TAGS — PERSIAN
# =====================================================

@register.inclusion_tag("RTL/blog/including/tags.html")
def blog_tags_fa():
    tags = (
        blog_Tag.objects
        .annotate(
            count=Count(
                "blog",
                filter=Q(blog__status="published")
            )
        )
        .filter(count__gt=0)
        .order_by("order")
    )
    return {"tags": tags}


# =====================================================
# BLOG TAGS — ENGLISH
# =====================================================

@register.inclusion_tag("LTR/blog/including/tags.html")
def blog_tags_en():
    tags = (
        blog_Tag.objects
        .annotate(
            count=Count(
                "blog",
                filter=Q(blog__status="published")
            )
        )
        .filter(count__gt=0)
        .order_by("order")
    )
    return {"tags": tags}