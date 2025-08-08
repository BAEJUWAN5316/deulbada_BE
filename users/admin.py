from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FarmerProfile


class FarmerProfileInline(admin.StackedInline):  # 혹은 TabularInline
    model = FarmerProfile
    can_delete = False
    verbose_name_plural = 'Farmer Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'is_active', 'is_staff', 'is_superuser', 'is_farmer', 'is_profile_completed')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_farmer')
    search_fields = ('email',)
    ordering = ('-id',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_farmer', 'is_profile_completed', 'groups', 'user_permissions')}),
        ('중요 날짜', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    inlines = [FarmerProfileInline]
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(User, UserAdmin)
