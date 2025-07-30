import re
from rest_framework import serializers
from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_password(self, value):
        # 길이 체크
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")

        # 영문, 숫자, 특수문자 각각 1개 이상 포함되어야 함
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("영문자를 최소 1자 이상 포함해야 합니다.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("숫자를 최소 1자 이상 포함해야 합니다.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("특수문자를 최소 1자 이상 포함해야 합니다.")

        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
