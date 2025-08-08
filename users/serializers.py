# users/serializers.py
from rest_framework import serializers
from .models import User
from posts.serializers import PostSerializer
from products.serializers import ProductSerializer

class MyProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts = PostSerializer(many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'profile_image', 'introduction',
            'follower_count', 'following_count',
            'posts', 'products'
        ]

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.followings.count()
