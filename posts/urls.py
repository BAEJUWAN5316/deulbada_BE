# posts/urls.py
from django.urls import path
from .views import PostUpdateDeleteView

urlpatterns = [
    path('<int:pk>/', PostUpdateDeleteView.as_view(), name='post-update-delete'),
]
