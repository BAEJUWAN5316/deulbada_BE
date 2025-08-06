# users/admin.py
from django.contrib import admin
from .models import User, UserProfile, Follow

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'username', 'email', 'is_staff', 'date_joined')
    search_fields = ('account_id', 'username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('-date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_farm_owner', 'is_farm_verified')
    search_fields = ('user__account_id',)
    list_filter = ('is_farm_owner', 'is_farm_verified')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__account_id', 'following__account_id')
    ordering = ('-created_at',)
