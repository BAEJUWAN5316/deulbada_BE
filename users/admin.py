from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('nickname', 'profile_image', 'introduction', 'followers')
        }),
    )
    list_display = ('username', 'nickname', 'email', 'is_staff')
    search_fields = ('username', 'nickname', 'email')
