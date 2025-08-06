from django.urls import path
from .views import MyPostsView

urlpatterns = [
    path('myposts/', MyPostsView.as_view()), 
]
