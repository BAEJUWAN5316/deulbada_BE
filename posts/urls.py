from django.urls import path
from .views import (
    PostListView, PostWriteView, PostDetailView, PostUpdateDeleteView,
    PostLikeToggleView,
    CommentCreateView, CommentUpdateDeleteView, CommentListView,
)

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("new/", PostWriteView.as_view()),
    path("posts/<int:id>/", PostDetailView.as_view()),
    path("posts/<int:id>/edit/", PostUpdateDeleteView.as_view()),
    
    path("posts/<int:post_id>/like/", PostLikeToggleView.as_view()),

    path("posts/<int:post_id>/comments/", CommentListView.as_view()),
    path("posts/<int:post_id>/comments/new/", CommentCreateView.as_view()),
    path("comments/<int:id>/", CommentUpdateDeleteView.as_view()),
]
