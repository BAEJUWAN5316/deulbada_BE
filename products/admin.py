# products/admin.py

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'seller', 'price', 'is_sold', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_sold', 'created_at')
