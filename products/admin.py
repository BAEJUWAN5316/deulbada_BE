from django.contrib import admin
from .models import Product # Removed ProductCategory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'name', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

# admin.site.register(ProductCategory) # Removed