# config/urls.py
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    # 헬스체크/루트
    path('', lambda request: HttpResponse("🚀 서버 정상 작동 중입니다!")),
    # Django Admin
    path('admin/', admin.site.urls),
    # 앱 URL
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),  
]
