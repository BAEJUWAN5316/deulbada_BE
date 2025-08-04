from django.urls import path
from .views import PostListView, PostCreateView

urlpatterns = [
     path('', PostListView.as_view(), name='post-list'),
    path('write/', PostCreateView.as_view(), name='post-write'),
]
