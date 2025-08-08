import re
from rest_framework import serializers
from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
