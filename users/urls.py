# users/urls.py
from django.urls import path
from .views import (
    UserSearchAPIView,
    MyPostsView,
    ReportCreateAPIView,
    SignupView,
)

urlpatterns = [
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('myposts/', MyPostsView.as_view(), name='user-myposts'),
    path('report/', ReportCreateAPIView.as_view(), name='user-report'),
    path('signup/', SignupView.as_view(), name='user-signup'),  
]
