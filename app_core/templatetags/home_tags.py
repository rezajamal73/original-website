# app_blog/templatetags/home_blog_tags.py

from django import template

from app_blog.models import blog

register = template.Library()


# =====================================================
# RECENT BLOGS - PERSIAN
# =====================================================

@register.inclusion_tag(
    "RTL/core/including/blog_recent_fa.html"
)
def home_blog_recent_fa():

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
    "LTR/core/including/blog_recent_en.html"
)
def home_blog_recent_en():

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