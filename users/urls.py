# users/urls.py
from django.urls import path
from .views import (
    ProfileRetrieveView,
    FollowersListView,
    FollowingListView,
    FollowToggleView,
)
from .views import UserSearchAPIView, MyPostsView, ReportCreateAPIView

urlpatterns = [
    path('profiles/<str:account_id>/', ProfileRetrieveView.as_view(), name='profile-detail'),
    path('profiles/<str:account_id>/followers/', FollowersListView.as_view(), name='profile-followers'),
    path('profiles/<str:account_id>/following/', FollowingListView.as_view(), name='profile-following'),
    path('profiles/<str:account_id>/follow/', FollowToggleView.as_view(), name='profile-follow-toggle'),
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('myposts/', MyPostsView.as_view(), name='user-myposts'),
    path('report/', ReportCreateAPIView.as_view(), name='user-report'),
]