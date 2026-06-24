
from django.contrib.sitemaps import Sitemap
from app_product.models import Product
from django.urls import reverse
class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Product.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, item):
        return reverse("app_product:product_single", kwargs={"pid": item.id})