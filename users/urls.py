from django.urls import path
from .views import (
    FollowCreateAPIView,
    UnfollowAPIView,
    FollowerListAPIView,
    FollowingListAPIView,
)

urlpatterns = [
    # 팔로우/언팔로우
    path('follow/', FollowCreateAPIView.as_view(), name='follow-user'),
    path('unfollow/<str:account_id>/', UnfollowAPIView.as_view(), name='unfollow-user'),

    # 팔로워/팔로잉 목록 조회
    path('followers/<str:account_id>/', FollowerListAPIView.as_view(), name='followers-list'),
    path('following/<str:account_id>/', FollowingListAPIView.as_view(), name='following-list'),
]
