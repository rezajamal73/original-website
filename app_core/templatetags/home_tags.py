from django import template
from app_blog.models import blog

register = template.Library()


# ======================
#   آخرین مقالات
# ======================
@register.inclusion_tag('RTL/core/including/blog_recent_fa.html')
def home_blog_recent_fa():
    blogs = blog.objects.filter(
        status="published"
    ).order_by(
        '-created_at_fa'
    )[:3]

    return {"blogs": blogs}
