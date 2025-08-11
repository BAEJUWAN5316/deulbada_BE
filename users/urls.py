from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupView, ProducerSignupView, CustomTokenObtainPairView,
    EmailCheckView, AccountIdCheckView,
    MyProfileView, ProfileSetupView, ProfileUpdateView, FarmOwnerProfileView,
    ProfileRetrieveView, FollowersListView, FollowingListView, FollowToggleView,
    UserSearchAPIView, MyPostsView, ReportCreateAPIView,
)

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("signup/producer/", ProducerSignupView.as_view()),
    path("login/", CustomTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    path("check-email/", EmailCheckView.as_view()),
    path("check-account-id/", AccountIdCheckView.as_view()),

    path("mypage/", MyProfileView.as_view()),
    path("mypage/profile/setup/", ProfileSetupView.as_view()),
    path("mypage/profile/", ProfileUpdateView.as_view()),
    path("mypage/farm/", FarmOwnerProfileView.as_view()),

    path("profiles/<str:account_id>/", ProfileRetrieveView.as_view()),
    path("profiles/<str:account_id>/followers/", FollowersListView.as_view()),
    path("profiles/<str:account_id>/following/", FollowingListView.as_view()),
    path("profiles/<str:account_id>/follow/", FollowToggleView.as_view()),

    path("search/", UserSearchAPIView.as_view()),
    path("myposts/", MyPostsView.as_view()),
    path("report/", ReportCreateAPIView.as_view()),
]
