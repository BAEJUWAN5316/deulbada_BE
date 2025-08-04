from rest_framework import serializers
from .models import User
import re

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'role',
            'representative_name',
            'business_registration_number',
            'business_document',
        ]

    def validate_password(self, value):
        # 영문 + 숫자 + 특수문자 + 8자 이상
        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("비밀번호에 영문자가 포함되어야 합니다.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("비밀번호에 숫자가 포함되어야 합니다.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("비밀번호에 특수문자가 포함되어야 합니다.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user