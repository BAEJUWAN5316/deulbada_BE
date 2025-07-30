from django.urls import path
from .views import UserListView,UserProfileView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('profile/', UserProfileView.as_view())
]
