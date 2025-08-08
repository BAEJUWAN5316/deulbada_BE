from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings # settings 임포트
from django.conf.urls.static import static # static 함수 임포트

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Swagger 설정
schema_view = get_schema_view(
   openapi.Info(
      title="들바다 API",
      default_version='v1',
      description="들바다 프로젝트 API 문서",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourdomain.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ✅ 서버 상태 확인용 루트
    path('', lambda request: HttpResponse("🚀 서버 정상 작동 중입니다!")),

    # ✅ 관리자
    path('admin/', admin.site.urls),

    # ✅ 사용자 기능
        path('api/uploads/', include('uploads.urls')),
    path('api/users/', include('users.urls')),

    path('posts/', include('posts.urls')),
    path('products/', include('products.urls')),
    path('chat/', include('chat.urls')),
    path('categories/', include('categories.urls')),

    # JWT 인증 관련
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # drf-yasg (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 개발 환경에서만 미디어 파일을 서빙하도록 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)