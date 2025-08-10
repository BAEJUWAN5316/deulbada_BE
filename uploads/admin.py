from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'uploaded_at', 'user')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)