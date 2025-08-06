from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    # ✅ 서버 상태 확인용 루트
    path('', lambda request: HttpResponse("🚀 서버 정상 작동 중입니다!")),

    # ✅ 관리자
    path('admin/', admin.site.urls),

    # ✅ 사용자 기능
    path('users/', include('users.urls')),

    # ✅ 게시글 기능 (활성화 시 사용)
     path('posts/', include('posts.urls')),

    # ✅ 제품 기능
    # path('products/', include('products.urls')),

    # ✅ 채팅 기능
    # path('chat/', include('chat.urls')),
]
