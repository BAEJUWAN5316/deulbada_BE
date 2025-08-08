from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserAdmin(BaseUserAdmin):
    model = User


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
