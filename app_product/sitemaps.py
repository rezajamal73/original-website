from django.contrib.sitemaps import Sitemap
from app_product.models import Product


class ProductSitemap(Sitemap):
    protocol = "https"

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return (
            Product.objects
            .filter(status="published")
            .select_related("category", "category2")
            .prefetch_related("tags")
            .order_by("-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()