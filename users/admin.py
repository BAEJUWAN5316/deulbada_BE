from django.contrib import admin
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