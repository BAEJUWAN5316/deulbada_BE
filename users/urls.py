from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignupViewSet, check_email  # check_email 뷰도 추가함

router = DefaultRouter()
router.register(r'signup', SignupViewSet, basename='signup')

urlpatterns = [
    path('', include(router.urls)),
    path('check-email/', check_email, name='check-email'),  # 이메일 중복 체크 API
]
