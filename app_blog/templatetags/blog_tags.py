# app_blog/templatetags/blog_tags.py

from django import template

from app_blog.models import (
    blog,
    blog_Category,
    blog_Tag
)

register = template.Library()


# =====================================================
# BLOG CATEGORIES
# =====================================================

@register.inclusion_tag(
    "RTL/blog/including/category_fa.html"
)
def blog_category_fa():

    blogs = blog.objects.filter(
        status="published"
    )

    categories = blog_Category.objects.all()

    data = [
        {
            "title": cat.title_fa,
            "slug": cat.slug,
            "count": blogs.filter(
                category=cat
            ).count()
        }
        for cat in categories
        if blogs.filter(
            category=cat
        ).exists()
    ]

    return {
        "categories": data
    }


# =====================================================
# BLOG CATEGORIES - ENGLISH
# =====================================================

@register.inclusion_tag(
    "LTR/blog/including/category_en.html"
)
def blog_category_en():

    blogs = blog.objects.filter(
        status="published"
    )

    categories = blog_Category.objects.all()

    data = [
        {
            "title": cat.title_en,
            "slug": cat.slug,
            "count": blogs.filter(
                category=cat
            ).count()
        }
        for cat in categories
        if blogs.filter(
            category=cat
        ).exists()
    ]

    return {
        "categories": data
    }


# =====================================================
# RECENT BLOGS - PERSIAN
# =====================================================

@register.inclusion_tag(
    "RTL/blog/including/recent_fa.html"
)
def blog_recent_fa():

    blogs = (
        blog.objects
        .filter(
            status="published"
        )
        .order_by(
            "-created_at_fa"
        )[:3]
    )

    return {
        "blogs": blogs
    }


# =====================================================
# RECENT BLOGS - ENGLISH
# =====================================================

@register.inclusion_tag(
    "LTR/blog/including/recent_en.html"
)
def blog_recent_en():

    blogs = (
        blog.objects
        .filter(
            status="published"
        )
        .order_by(
            "-created_at_en"
        )[:3]
    )

    return {
        "blogs": blogs
    }


# =====================================================
# BLOG TAGS - PERSIAN
# =====================================================

@register.inclusion_tag(
    "RTL/blog/including/tags.html"
)
def blog_tags_fa():

    tags = (
        blog_Tag.objects
        .filter(
            blog__status="published"
        )
        .distinct()
    )

    return {
        "tags": tags
    }


# =====================================================
# BLOG TAGS - ENGLISH
# =====================================================

@register.inclusion_tag(
    "LTR/blog/including/tags.html"
)
def blog_tags_en():

    tags = (
        blog_Tag.objects
        .filter(
            blog__status="published"
        )
        .distinct()
    )

    return {
        "tags": tags
    }