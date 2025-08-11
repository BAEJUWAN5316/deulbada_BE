# apps/social/serializers.py
from django.db.models import Count, Exists, OuterRef
from rest_framework import serializers
from django.contrib.auth import get_user_model
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
