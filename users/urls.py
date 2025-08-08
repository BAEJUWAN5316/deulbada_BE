# users/urls.py
from django.urls import path
from .views import MyProfileView

urlpatterns = [
    path('mypage/', MyProfileView.as_view(), name='my-profile'),
]
