from django.contrib.sitemaps import Sitemap
from app_blog.models import blog
from django.urls import reverse
class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return blog.objects.filter(status="published")
    def lastmod(self, obj):
        return obj.publish_date_fa

    def location(self, item):
        return reverse("app_blog:blog_single", kwargs={"pid": item.id})