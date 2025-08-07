from django.urls import path
from .views import UserSearchAPIView, MyPostsView, ReportCreateAPIView

urlpatterns = [
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('myposts/', MyPostsView.as_view(), name='user-myposts'),
    path('report/', ReportCreateAPIView.as_view(), name='user-report'),
]