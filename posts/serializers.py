from rest_framework import serializers
from .models import Post, Comment

# 🔹 게시글 목록 조회용
class PostListSerializer(serializers.ModelSerializer):
    account_id = serializers.CharField(source='author.account_id')
    username = serializers.CharField(source='author.username')
    profile_image = serializers.URLField(source='author.userprofile.profile_image')

    class Meta:
        model = Post
        fields = ['id', 'account_id', 'username', 'profile_image', 'content', 'image_urls', 'created_at']

# 🔹 게시글 작성용 (write)
class PostWriteSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, default=list
    )

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_urls']

# 🔹 게시글 상세 조회용
class PostDetailSerializer(serializers.ModelSerializer):
    account_id = serializers.CharField(source='author.account_id')
    username = serializers.CharField(source='author.username')
    profile_image = serializers.URLField(source='author.userprofile.profile_image')

    class Meta:
        model = Post
        fields = ['id', 'account_id', 'username', 'profile_image', 'content', 'image_urls', 'created_at']

# 🔹 댓글/대댓글 공용 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'post', 'parent_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
