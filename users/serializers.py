# users/serializers.py

from rest_framework import serializers
from .models import User, FarmerProfile
import re


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ['representative_name', 'business_number', 'registration_image']


class FarmerSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    farmer_profile = FarmerProfileSerializer()

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'farmer_profile']
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
            raise serializers.ValidationError("영문자를 포함해야 합니다.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("숫자를 포함해야 합니다.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("특수문자를 포함해야 합니다.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('farmer_profile')
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_farmer=True,
            is_active=False  # 이메일 인증 등 있으면
        )
        FarmerProfile.objects.create(user=user, **profile_data)
        return user
