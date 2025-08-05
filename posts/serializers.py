from rest_framework import serializers
from .models import Post

class PostWriteSerializer(serializers.ModelSerializer):
    # 🔹 작성자 username 표시 (읽기 전용)
    author = serializers.CharField(source='author.username', read_only=True)

    # 🔹 이미지 리스트 처리 (기본 빈 리스트, 최대 10장 제한은 필요시 가능)
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list
    )

   

class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    like_count = serializers.IntegerField(source='like_set.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image_urls', 'created_at', 'like_count']
