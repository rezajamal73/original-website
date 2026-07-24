from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from app_product.models import Product
from app_blog.models import blog
from app_news.models import News



# صفحات ثابت سایت
class StaticViewSitemap(Sitemap):

    protocol = "https"
    priority = 0.8
    changefreq = "weekly"

    def items(self):

        urls = [

            "app_core:home",
            "app_core:about",
            "app_core:contact",

            "app_product:product_list",
            "app_blog:blog_home",
            "app_news:news_home",

            "app_resume:resume",

            "app_media:home",
            "app_catalog:catalog",

        ]

        valid_urls = []

        for url in urls:

            try:
                reverse(url)
                valid_urls.append(url)

            except Exception:
                continue

        return valid_urls


    def location(self, item):

        return reverse(item)


# محصولات
class ProductSitemap(Sitemap):

    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(
            status="published"
        )

    def lastmod(self, obj):
        return getattr(
            obj,
            "updated_at",
            None
        )

    def location(self, obj):
        return obj.get_absolute_url()



# مقالات
class BlogSitemap(Sitemap):

    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return blog.objects.filter(
            status="published"
        )

    def lastmod(self, obj):
        return getattr(
            obj,
            "updated_at",
            None
        )

    def location(self, obj):
        return reverse(
            "app_blog:blog_single",
            kwargs={"pid": obj.id}
        )



# اخبار
class NewsSitemap(Sitemap):

    protocol = "https"
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return News.objects.filter(
            status="published"
        )

    def lastmod(self, obj):
        return getattr(
            obj,
            "updated_at",
            None
        )

    def location(self, obj):
        return reverse(
            "app_news:news_single",
            kwargs={"pid": obj.id}
        )