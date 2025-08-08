from django.urls import path
from .views import SignupView, EmailCheckView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('check-email/', EmailCheckView.as_view(), name='check-email'),  # api 이메일 중복 
]
