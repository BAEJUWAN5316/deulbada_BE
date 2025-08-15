from django.contrib import admin
from .models import User, UserProfile, Report

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'account_id', 'username', 'nickname', 'email', 'is_farm_owner', 'is_farm_verified', 'date_joined')
    search_fields = ('account_id', 'username', 'nickname', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_farm_owner', 'is_farm_verified')
    ordering = ('-date_joined',)
    readonly_fields = ()  

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_farm_owner', 'is_farm_verified', 'created_at')
    search_fields = (
        'user__account_id', 'user__username', 'user__nickname', 'user__email',
        'ceo_name', 'business_number'
    )
    list_filter = ('is_farm_owner', 'is_farm_verified')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_user', 'status', 'reason_short', 'created_at')
    search_fields = (
        'reporter__email', 'reporter__account_id', 'reporter__username', 'reporter__nickname',
        'target_user__email', 'target_user__account_id', 'target_user__username', 'target_user__nickname',
        'reason'
    )
    list_filter = ('status',)
    ordering = ('-created_at',)
    list_editable = ('status',)  
    def reason_short(self, obj):
        if not obj.reason:
            return ''
        return (obj.reason[:30] + '...') if len(obj.reason) > 30 else obj.reason
    reason_short.short_description = '신고 사유'
