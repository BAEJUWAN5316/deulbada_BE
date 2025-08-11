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

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserAdmin(BaseUserAdmin):
    model = User


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)

from .models import User, UserProfile, Report

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'username', 'email')
    search_fields = ('account_id', 'username', 'email')
    list_filter = ('is_staff', 'is_superuser')
    ordering = ('-date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_farm_owner', 'is_farm_verified')
    search_fields = ('user__account_id',)
    list_filter = ('is_farm_owner', 'is_farm_verified')
    ordering = ('-created_at',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_user', 'status', 'created_at')
    search_fields = ('reporter__username', 'target_user__username')
    ordering = ('-created_at',)
    list_editable = ('status',)

    def reason_short(self, obj):
        return obj.reason[:30] + '...' if len(obj.reason) > 30 else obj.reason
    reason_short.short_description = '신고 사유'