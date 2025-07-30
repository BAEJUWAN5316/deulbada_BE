
from django.urls import path
from .views import UserSignupView  # 회원가입 뷰를 작성한 경우

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
]
