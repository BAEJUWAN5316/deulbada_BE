from rest_framework import serializers
from .models import Post

class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    image_urls = serializers.ListField(
        child=serializers.URLField(), required=False, default=list
    )

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_urls']

class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_urls', 'created_at']
