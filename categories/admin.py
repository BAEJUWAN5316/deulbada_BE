from django.contrib import admin
# from mptt.admin import MPTTModelAdmin # REMOVED
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): # Changed to admin.ModelAdmin
    # mptt_indent_field = "name" # REMOVED
    list_display = ('name', 'type', 'created_at', 'updated_at') # Removed 'parent'
    list_filter = ('type',)
    search_fields = ('name',)