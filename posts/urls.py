from django.urls import path
from .views import PostListView, PostWriteView, PostLikeToggleView

urlpatterns = [
    # 전체 게시글 조회
    path('', PostListView.as_view(), name='post-list'),

    # 게시글 작성 (write)
    path('write/', PostWriteView.as_view(), name='post-write'),

    # 게시글 좋아요 / 좋아요 취소
    path('<int:post_id>/like/', PostLikeToggleView.as_view(), name='post-like'),
]
