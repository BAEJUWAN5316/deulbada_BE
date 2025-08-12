# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Follow, Report

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'account_id', 'username', 'is_farm_owner', 'is_farm_verified', 'is_staff')
    search_fields = ('email', 'account_id', 'username')
    ordering = ('-id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('account_id', 'username', 'nickname', 'introduction', 'profile_image',
                                'is_profile_completed', 'is_farm_owner', 'is_farm_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'account_id', 'username')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_farm_owner', 'is_farm_verified', 'created_at')
    search_fields = ('user__email', 'user__account_id')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__email', 'following__email')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_user', 'status', 'created_at')
    search_fields = ('reporter__email', 'target_user__email')
    list_filter = ('status',)
