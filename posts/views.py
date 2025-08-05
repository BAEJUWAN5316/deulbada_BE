from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Post, Like, Comment
from .serializers import (
    PostListSerializer,
    PostWriteSerializer,
    CommentSerializer,
    PostDetailSerializer
)
from django.shortcuts import get_object_or_404

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

# 🔹 게시글 상세 조회
class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'id'

# 🔹 게시글 수정 / 삭제
class PostUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("작성자만 수정 가능")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("작성자만 삭제 가능")
        instance.delete()

# 🔹 게시글 좋아요/취소 토글
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            return Response({"message": "좋아요 완료", "post_id": post.id}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            return Response({"message": "좋아요 취소", "post_id": post.id}, status=status.HTTP_200_OK)

# 🔹 댓글/대댓글 작성
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        content = request.data.get('content')
        parent_id = request.data.get('parent_id')

        if not content:
            return Response({"error": "내용이 비어있습니다."}, status=400)

        comment = Comment(post=post, user=request.user, content=content)

        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
            if not parent_comment:
                return Response({"error": "부모 댓글 없음"}, status=404)
            comment.parent = parent_comment

        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=201)

# 🔹 댓글 수정 / 삭제
class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("작성자만 수정 가능")
        serializer.save()

    def perform_destroy(self, instance):
        post_owner = instance.post.author
        if instance.user != self.request.user and post_owner != self.request.user:
            raise PermissionDenied("작성자 또는 게시글 작성자만 삭제 가능")
        instance.delete()

# 🔹 게시글에 달린 댓글 목록 조회 (페이징)
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id, parent__isnull=True).order_by('-created_at')
