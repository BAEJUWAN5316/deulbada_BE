# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Follow, Report


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 목록
    list_display = (
        'id', 'email', 'account_id', 'username', 'nickname',
        'is_farm_owner', 'is_farm_verified', 'is_staff'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_farm_owner', 'is_farm_verified')
    search_fields = ('email', 'account_id', 'username', 'nickname')
    ordering = ('-id',)
    date_hierarchy = 'date_joined'

    # 폼
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {
            'fields': (
                'account_id', 'username', 'nickname', 'introduction', 'profile_image',
                'is_profile_completed', 'is_farm_owner', 'is_farm_verified'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'account_id', 'username', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    # 읽기전용
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'is_farm_owner', 'is_farm_verified',
        'ceo_name', 'phone', 'business_number',
        'address_postcode', 'created_at'
    )
    list_filter = ('is_farm_owner', 'is_farm_verified')
    search_fields = ('user__email', 'user__account_id', 'user__username', 'ceo_name', 'business_number')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__email', 'follower__account_id', 'following__email', 'following__account_id')
    list_select_related = ('follower', 'following')
    raw_id_fields = ('follower', 'following')
    readonly_fields = ('created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'target_user', 'status', 'reason_short', 'created_at')
    list_filter = ('status',)
    search_fields = ('reporter__email', 'reporter__account_id', 'target_user__email', 'target_user__account_id', 'reason')
    list_select_related = ('reporter', 'target_user')
    readonly_fields = ('created_at',)

    @admin.display(description='신고 사유')
    def reason_short(self, obj):
        if not obj.reason:
            return ''
        return (obj.reason[:30] + '...') if len(obj.reason) > 30 else obj.reason
