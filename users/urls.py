from django.urls import path
from .views import UserSearchAPIView

urlpatterns = [
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
]
