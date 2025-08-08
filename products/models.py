from django.db import models
from django.conf import settings
from core.models.base import TimeStampedModel

class Product(TimeStampedModel):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    image_urls = models.URLField(default=list, blank=True)
    variety = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    product_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"[{self.name}] 판매자: {self.seller.username}"

class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_categories')
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"