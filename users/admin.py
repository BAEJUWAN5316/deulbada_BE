from django.contrib import admin
from .models import User, Report

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_farm_owner', 'is_farm_verified', 'is_active', 'date_joined')  # ✅ is_farm_verified 추가
    search_fields = ('username', 'email')
    list_filter = ('is_farm_owner', 'is_farm_verified', 'is_active')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_user', 'reason_short', 'status', 'created_at')  
    search_fields = ('reporter__username', 'target_user__username', 'reason')
    list_filter = ('status', 'created_at')  # 
    ordering = ('-created_at',)
    list_editable = ('status',)  

    def reason_short(self, obj):
        return obj.reason[:30] + '...' if len(obj.reason) > 30 else obj.reason
    reason_short.short_description = '신고 사유'
