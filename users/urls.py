from django.urls import path
from .views import MyPostsView,MyPostDetailView

urlpatterns = [
    path('myposts/', MyPostsView.as_view()), 
    path('myposts/<int:pk>/', MyPostDetailView.as_view()),
]
