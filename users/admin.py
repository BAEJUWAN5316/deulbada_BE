from django.contrib import admin
from .models import User, UserProfile, Follow

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Follow)
