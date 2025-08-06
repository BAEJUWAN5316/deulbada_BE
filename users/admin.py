from django.contrib import admin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'username', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('account_id', 'username')  
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_farm_owner', 'is_farm_verified', 'created_at')
    search_fields = ('user__account_id', 'user__username')  
    list_filter = ('is_farm_owner', 'is_farm_verified', 'created_at')
    ordering = ('-created_at',)
