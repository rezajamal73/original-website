from django import template
from app_blog.models import blog, blog_Category, blog_Tag

register = template.Library()


# ======================
#   دسته‌بندی‌ها
# ======================
@register.inclusion_tag('RTL/blog/including/category_fa.html')
def blog_category_fa():
    blogs = blog.objects.filter(status="published")
    categories = blog_Category.objects.all()

    # لیست تمیز شامل category + count
    data = [
        {
            "title_fa": cat.title_fa,
            "slug": cat.slug,
            "count": blogs.filter(category=cat).count()
        }
        for cat in categories
        if blogs.filter(category=cat).exists()
    ]

    return {"categories": data}


# ======================
#   آخرین مقالات
# ======================
@register.inclusion_tag('RTL/blog/including/recent_fa.html')
def blog_recent_fa():
    blogs = blog.objects.filter(
        status="published"
    ).order_by(
        '-created_at_fa'
    )[:3]

    return {"blogs": blogs}


# ======================
#   برچسب‌ها
# ======================
@register.inclusion_tag('RTL/blog/including/tags.html')
def blog_tags_fa():
    tags = blog_Tag.objects.filter(
        blog__status="published"
    ).distinct()
    return {"tags": tags}
