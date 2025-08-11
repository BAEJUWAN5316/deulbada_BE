from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from .models import Post, Like, Comment
from .serializers import (
    PostListSerializer, PostWriteSerializer, PostDetailSerializer, CommentSerializer
)

User = get_user_model()

class SmallPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 50

def _truthy(v): return str(v).lower() in {"1","true","t","yes","y","on"}

# 목록 (페이지네이션 + 유저/사진 필터 + 집계)
class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = (Post.objects.select_related("author")
              .annotate(like_count=Count("likes", distinct=True),
                        comment_count=Count("comments", distinct=True),
                        author_is_farm_verified=F("author__is_farm_verified"))
              .order_by("-created_at"))
        user_key = self.request.query_params.get("user")
        if user_key:
            if str(user_key).isdigit():
                user = User.objects.filter(Q(id=user_key) | Q(account_id__iexact=user_key)).first()
            else:
                user = User.objects.filter(Q(account_id__iexact=user_key) | Q(username__iexact=user_key)).first()
            qs = qs.filter(author=user) if user else Post.objects.none()
        if _truthy(self.request.query_params.get("photos","")):
            qs = qs.filter(Q(image__isnull=False) | Q(images__isnull=False)).distinct()
        return qs

# 작성 (멀티파트)
class PostWriteView(generics.CreateAPIView):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Title of the post', required=True),
            openapi.Parameter('content', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Content of the post', required=True),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Single image file for the post'),
            openapi.Parameter('images_add', openapi.IN_FORM, type=openapi.TYPE_FILE, description='List of additional image files for the post', collection_format='multi'),
            openapi.Parameter('image_ids_delete', openapi.IN_FORM, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of image IDs to delete from the post'),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# 상세 (집계 포함)
class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    def get_queryset(self):
        return (Post.objects.select_related("author")
                .annotate(like_count=Count("likes", distinct=True),
                          comment_count=Count("comments", distinct=True),
                          author_is_farm_verified=F("author__is_farm_verified")))

# 수정/삭제 (작성자만)
class PostUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "id"

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Title of the post'),
            openapi.Parameter('content', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Content of the post'),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Single image file for the post'),
            openapi.Parameter('images_add', openapi.IN_FORM, type=openapi.TYPE_FILE, description='List of additional image files for the post', collection_format='multi'),
            openapi.Parameter('image_ids_delete', openapi.IN_FORM, type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of image IDs to delete from the post'),
        ]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.all()
    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("작성자만 수정 가능합니다.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("작성자만 삭제 가능합니다.")
        instance.delete()



# 좋아요 토글
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created: return Response({"message":"좋아요 완료","post_id":post.id}, status=status.HTTP_201_CREATED)
        like.delete(); return Response({"message":"좋아요 취소","post_id":post.id})

# 댓글 생성(대댓글 포함)
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        content = request.data.get("content")
        parent_id = request.data.get("parent_id")
        if not content:
            return Response({"error":"내용이 비어있습니다."}, status=400)
        c = Comment(post=post, user=request.request.user, content=content)
        if parent_id:
            parent = Comment.objects.filter(id=parent_id, post=post).first()
            if not parent:
                return Response({"error":"부모 댓글 없음"}, status=404)
            c.parent = parent
        c.save()
        # reply_count annotate
        c.reply_count = c.replies.count()
        return Response(CommentSerializer(c).data, status=201)

# 댓글 수정/삭제
class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    def perform_update(self, serializer):
        c = self.get_object()
        if c.user != self.request.user:
            raise PermissionDenied("작성자만 수정 가능")
        serializer.save()
    def perform_destroy(self, instance):
        owner = instance.post.author
        if instance.user != self.request.user and owner != self.request.user:
            raise PermissionDenied("작성자 또는 게시글 작성자만 삭제 가능")
        instance.delete()

# 특정 게시글의 댓글 목록(부모 댓글만) — 페이지네이션
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SmallPagination
    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return (Comment.objects.filter(post_id=post_id, parent__isnull=True)
                .annotate(reply_count=Count("replies", distinct=True))
                .order_by("-created_at"))