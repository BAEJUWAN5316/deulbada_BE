from django.urls import path
from .views import MyProfileView, FollowToggleView,FollowerListView, FollowingListView




urlpatterns = [
    # ✅ 내 프로필 조회/수정
    path('me/', MyProfileView.as_view(), name='my-profile'),

    # ✅ 팔로우 / 언팔로우 토글 API
    path('follow/<str:account_id>/', FollowToggleView.as_view(), name='follow-toggle'),

    path('followers/<str:account_id>/', FollowerListView.as_view(), name='follower-list'),

    path('following/<str:account_id>/', FollowingListView.as_view(), name='following-list'),
]
