from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']