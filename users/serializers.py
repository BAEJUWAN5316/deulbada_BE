from rest_framework import serializers
from .models import UserProfile, User

# ✅ 팔로워/팔로잉 목록 조회용 (당신이 만든 것)
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['account_id', 'username']

# ✅ 프로필 정보용 시리얼라이저
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'is_farm_owner', 'is_farm_verified']

# ✅ 전체 프로필 조회/수정 시 사용
class MyProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile')

    class Meta:
        model = User
        fields = ['account_id', 'username', 'email', 'profile']
