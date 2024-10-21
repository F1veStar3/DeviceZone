from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def location(self, item):
        return reverse('product_detail', kwargs={'pk': item.id})

    def lastmod(self, item):
        return item.updated_at