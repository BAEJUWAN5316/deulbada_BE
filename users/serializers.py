# users/serializers.py
from rest_framework import serializers
from .models import User, UserProfile, Report
from posts.models import Post
from posts.serializers import PostListSerializer 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account_id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'is_farm_owner', 'is_farm_verified']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class UserDetailSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'account_id', 'username', 'email', 'posts']

    def get_posts(self, obj):
        posts = Post.objects.filter(author=obj)
        return PostListSerializer(posts, many=True).data