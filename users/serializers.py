from rest_framework import serializers
from .models import User, UserProfile, Report
from posts.models import Post
from posts.serializers import PostListSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account_id', 'username', 'email']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # 프로필(소유주 여부)은 UserProfile에 저장
    is_farm_owner = serializers.BooleanField(required=True)

    class Meta:
        model = User
        # ✅ 이메일이 로그인 아이디이므로 email 필수
        fields = ['email', 'password', 'account_id', 'username', 'is_farm_owner']

    def create(self, validated_data):
        is_farm_owner = validated_data.pop('is_farm_owner')
        password = validated_data.pop('password')

        # UserManager.create_user(email, password, **extra_fields) 사용
        user = User.objects.create_user(password=password, **validated_data)

        # 프로필 생성/업데이트
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'is_farm_owner': is_farm_owner}
        )
        return user


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
