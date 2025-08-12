from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, PostImage, Comment

User = get_user_model()


class AuthorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "account_id", "username", "profile_image", "is_farm_verified"]


class PostImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ["id", "url", "created_at"]

    def get_url(self, obj):
        return getattr(obj.image, "url", None)


class _ImagesMixin(serializers.ModelSerializer):
    image_urls = serializers.SerializerMethodField()

    def get_image_urls(self, obj):
        urls = []
        if getattr(obj, "image", None):
            try:
                urls.append(obj.image.url)
            except Exception:
                pass
        for p in obj.images.all():
            try:
                urls.append(p.image.url)
            except Exception:
                pass
        # 중복 제거(순서 유지)
        return list(dict.fromkeys(urls))


class PostListSerializer(_ImagesMixin):
    author = AuthorMiniSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    author_is_farm_verified = serializers.BooleanField(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)  

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "content",
            "created_at",
            "like_count",
            "comment_count",
            "author_is_farm_verified",
            "is_liked",       
            "image_urls",
        ]


class PostDetailSerializer(PostListSerializer):
    images = PostImageSerializer(many=True, read_only=True)

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["images"]


# 단순화된 PostWriteSerializer - 문제 필드들 제거
class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "image"]  # 기본 필드들만

    def validate_image(self, img):
        """메인 이미지 크기 검증"""
        max_size = 5 * 1024 * 1024
        if img and hasattr(img, "size") and img.size > max_size:
            raise serializers.ValidationError("이미지 크기는 5MB를 초과할 수 없습니다.")
        return img


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorMiniSerializer(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "content", "parent", "created_at", "reply_count"]
        read_only_fields = ["post", "user", "reply_count"]
