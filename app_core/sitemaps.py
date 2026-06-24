from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'
    def items(self):
        return ['app_core:home','app_core:about','app_core:contact']
    def location(self, item):
        return reverse(item)