from rest_framework import generics, permissions
from posts.models import Post
from posts.serializers import PostSerializer

# 1. 내가 쓴 글 리스트 조회
class MyPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_at')


# 2. 내가 쓴 글 상세 조회 + 수정 + 삭제
class MyPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
