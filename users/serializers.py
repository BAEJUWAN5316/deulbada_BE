import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# users/serializers.py
from rest_framework import serializers
from .models import User

# 프로필 설정에 사용될 Serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['account_id', 'username', 'bio', 'profile_image']

    def validate_profile_image(self, value):
        max_size = 5 * 1024 * 1024  # 5MB 제한
        if value.size > max_size:
            raise serializers.ValidationError("이미지 파일은 5MB 이하만 업로드 가능합니다.")
        return value

    def update(self, instance, validated_data):
        instance.account_id = validated_data.get('account_id', instance.account_id)
        instance.username = validated_data.get('username', instance.username)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.is_profile_completed = True
        instance.save()
        return instance


# 다른 앱(ex. chat)에서 사용할 UserSerializer (공용)
from .models import User
from posts.serializers import PostSerializer
from products.serializers import ProductSerializer
from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
from django.db.models import Count, Exists, OuterRef
from django.contrib.auth import get_user_model
from .models import User, UserProfile, Report
from posts.models import Post
from posts.serializers import PostListSerializer 
from .models import Follow

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'account_id', 'username', 'profile_image']
        fields = ['id', 'username', 'email']

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
        fields = ['id', 'account_id', 'username', 'email', 'posts']

    def get_posts(self, obj):
        posts = Post.objects.filter(author=obj)
        return PostListSerializer(posts, many=True).data
    
from .models import Follow

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    # 목록 화면용 요약
    class Meta:
        model = User
        fields = ['account_id', 'username', 'profile_image', 'bio', 'is_farm_owner']


class ProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)  # 로그인 유저 기준

    class Meta:
        model = User
        fields = [
            'account_id', 'username', 'profile_image', 'bio', 'is_farm_owner',
            'follower_count', 'following_count', 'is_following'
        ]


def annotated_profile_qs(request_user):
    """
    프로필/목록 공통 어노테이션:
    - follower_count: 나를 팔로우하는 수
    - following_count: 내가 팔로우하는 수
    - is_following: (로그인 유저 -> 해당 사용자) 팔로우 여부
    """
    qs = User.objects.all().annotate(
        follower_count=Count('followed_by', distinct=True),
        following_count=Count('following', distinct=True),
    )

    if request_user and request_user.is_authenticated:
        qs = qs.annotate(
            is_following=Exists(
                Follow.objects.filter(
                    follower=request_user,
                    following=OuterRef('pk'),
                )
            )
        )
    else:
        # 비로그인 시 False 고정
        qs = qs.annotate(is_following=Exists(Follow.objects.none()))

    return qs
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("영문자를 최소 1자 이상 포함해야 합니다.")

        if not re.search(r'\d', value):
            raise serializers.ValidationError("숫자를 최소 1자 이상 포함해야 합니다.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("특수문자를 최소 1자 이상 포함해야 합니다.")

        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
from django.contrib.auth import authenticate

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "이메일 또는 비밀번호가 잘못되었습니다."})

        data = super().validate(attrs)
        data.update({
            "user_id": self.user.id,
            "email": self.user.email,
            "message": "로그인 성공"
        })
        return data
