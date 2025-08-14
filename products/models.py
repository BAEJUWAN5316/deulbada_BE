from django.db import models
from django.conf import settings
from core.models.base import TimeStampedModel
from categories.models import Category # Import Category to get ALL_CATEGORIES

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="태그 이름")

    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()
    is_sold = models.BooleanField(default=False)
    image_urls = models.URLField(blank=True)
    variety = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    sales_link = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True, help_text="상품에 연결된 태그 목록")
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products') # New field

    def __str__(self):
        return f"[{self.name}] 판매자: {self.seller.username}"

# ProductCategory model is removed
# class ProductCategory(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_categories')
#     category = models.ForeignKey('categories.Category', on_delete=models.CASCADE)
