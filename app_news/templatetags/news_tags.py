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

    data = []
    for cat in categories:
        count = blogs.filter(category=cat).count()
        if count > 0:
            data.append({
                "title_fa": cat.title_fa,
                "slug": cat.slug,
                "count": count,
            })

    return {"categories": data}


# ======================
#   آخرین مقالات
# ======================
@register.inclusion_tag('RTL/blog/including/recent_fa.html')
def blog_recent_fa():
    blogs = blog.objects.filter(status="published").order_by(
        "-publish_date_fa", "-publish_time"
    )[:3]

    return {"blogs": blogs}


# ======================
#   برچسب‌ها
# ======================
@register.inclusion_tag('RTL/blog/including/tags.html')
def blog_tags_fa():
    tags = blog_Tag.objects.filter(
        blog__status="published"   # فقط برچسب‌هایی که پست منتشر شده دارند
    ).distinct()

    return {"tags": tags}
