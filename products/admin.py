from django.contrib import admin
from .models import Product, ProductCategory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'seller__username']
    ordering = ['-created_at']

admin.site.register(ProductCategory)
