from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'is_active', 'is_staff')
    search_fields = ('email',)
    ordering = ('-id',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('권한'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('마지막 로그인'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
