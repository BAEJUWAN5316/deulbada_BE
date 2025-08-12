from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination

from .models import Post, Like, Comment, PostImage
from .serializers import (
    PostListSerializer, PostWriteSerializer, PostDetailSerializer, CommentSerializer
)

User = get_user_model()

class SmallPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 50

def _truthy(v): return str(v).lower() in {"1","true","t","yes","y","on"}

class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = (Post.objects.select_related("author").prefetch_related("images")
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

class PostWriteView(generics.CreateAPIView):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        # 기본 게시글 생성
        post = serializer.save(author=self.request.user)
        
        # 추가 이미지들 처리
        self._handle_additional_images(post)
    
    def _handle_additional_images(self, post):
        """추가 이미지들을 처리하는 헬퍼 메서드"""
        additional_images = self.request.FILES.getlist('images_add')
        
        # 이미지 개수 검증
        current_count = 1 if post.image else 0  # 메인 이미지
        additional_count = len(additional_images)
        total_count = current_count + additional_count
        
        if total_count > 5:
            raise ValidationError("이미지는 최대 5개까지 업로드 가능합니다.")
        if additional_count > 4:
            raise ValidationError("추가 이미지는 최대 4개까지 가능합니다.")
        
        # 이미지 크기 검증 및 생성
        max_size = 5 * 1024 * 1024
        for img in additional_images:
            if img.size > max_size:
                raise ValidationError(f"이미지 '{img.name}'의 크기는 5MB를 초과할 수 없습니다.")
        
        # PostImage 객체들 생성
        new_images = [
            PostImage(post=post, image=img)
            for img in additional_images
        ]
        PostImage.objects.bulk_create(new_images)

class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    def get_queryset(self):
        return (Post.objects.select_related("author").prefetch_related("images")
                .annotate(like_count=Count("likes", distinct=True),
                          comment_count=Count("comments", distinct=True),
                          author_is_farm_verified=F("author__is_farm_verified")))

class PostUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "id"
    
    def get_queryset(self):
        return Post.objects.all().prefetch_related("images")
    
    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("작성자만 수정 가능합니다.")
        
        # 기본 필드들 업데이트
        serializer.save()
        
        # 이미지 삭제 처리
        self._handle_image_deletion(post)
        
        # 추가 이미지 처리
        self._handle_additional_images_update(post)
    
    def _handle_image_deletion(self, post):
        """삭제할 이미지들 처리"""
        delete_ids = self.request.data.get('image_ids_delete', '')
        if delete_ids:
            # 콤마로 구분된 문자열을 리스트로 변환
            if isinstance(delete_ids, str):
                delete_ids = [int(id.strip()) for id in delete_ids.split(',') if id.strip().isdigit()]
            elif isinstance(delete_ids, list):
                delete_ids = [int(id) for id in delete_ids if str(id).isdigit()]
            
            if delete_ids:
                PostImage.objects.filter(post=post, id__in=delete_ids).delete()
    
    def _handle_additional_images_update(self, post):
        """수정 시 추가 이미지들 처리"""
        additional_images = self.request.FILES.getlist('images_add')
        
        if not additional_images:
            return
        
        # 현재 이미지 개수 계산
        current_main = 1 if post.image else 0
        current_additional = post.images.count()
        new_additional = len(additional_images)
        total_count = current_main + current_additional + new_additional
        
        if total_count > 5:
            raise ValidationError("이미지는 최대 5개까지 업로드 가능합니다.")
        if new_additional > 4:
            raise ValidationError("추가 이미지는 최대 4개까지 가능합니다.")
        
        # 이미지 크기 검증 및 생성
        max_size = 5 * 1024 * 1024
        for img in additional_images:
            if img.size > max_size:
                raise ValidationError(f"이미지 '{img.name}'의 크기는 5MB를 초과할 수 없습니다.")
        
        # PostImage 객체들 생성
        new_images = [
            PostImage(post=post, image=img)
            for img in additional_images
        ]
        PostImage.objects.bulk_create(new_images)
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("작성자만 삭제 가능합니다.")
        instance.delete()

# 개별 이미지 삭제 (X 버튼)
class PostImageDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, post_id, image_id):
        img = get_object_or_404(PostImage, id=image_id, post_id=post_id)
        if img.post.author != request.user:
            raise PermissionDenied("작성자만 삭제 가능합니다.")
        img.delete()
        return Response(status=204)

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
        c = Comment(post=post, user=request.user, content=content)
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