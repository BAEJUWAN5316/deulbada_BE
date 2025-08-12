# posts/urls.py
from django.urls import path
from .views import (
    PostListView, PostWriteView, PostDetailView, PostUpdateDeleteView,
    PostImageDeleteView, PostLikeToggleView,
    CommentCreateView, CommentUpdateDeleteView, CommentListView,
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),                                   # GET   /posts/
    path("new/", PostWriteView.as_view(), name="create"),                            # POST  /posts/new/
    path("<int:id>/", PostDetailView.as_view(), name="detail"),                      # GET   /posts/<id>/
    path("<int:id>/edit/", PostUpdateDeleteView.as_view(), name="edit"),             # PUT/PATCH/DELETE /posts/<id>/edit/
    path("<int:post_id>/images/<int:image_id>/", PostImageDeleteView.as_view(),
         name="image-delete"),                                                       # DELETE /posts/<post_id>/images/<image_id>/
    path("<int:post_id>/like/", PostLikeToggleView.as_view(), name="like-toggle"),   # POST  /posts/<post_id>/like/

    path("<int:post_id>/comments/", CommentListView.as_view(), name="comments"),     # GET   /posts/<post_id>/comments/
    path("<int:post_id>/comments/new/", CommentCreateView.as_view(),
         name="comment-create"),                                                     # POST  /posts/<post_id>/comments/new/
    path("comments/<int:id>/", CommentUpdateDeleteView.as_view(),
         name="comment-edit"),                                                       # PUT/PATCH/DELETE /posts/comments/<id>/
]