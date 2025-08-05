from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Post, Like
from .serializers import PostListSerializer, PostWriteSerializer

# 🔹 전체 게시글 목록 조회
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostListSerializer

# 🔹 게시글 작성 (write)
class PostWriteView(generics.CreateAPIView):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# 🔹 게시글 좋아요/취소 토글
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "게시글 없음"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            return Response({
                "message": "좋아요 완료",
                "post_id": post.id
            }, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            return Response({
                "message": "좋아요 취소",
                "post_id": post.id
            }, status=status.HTTP_200_OK)
