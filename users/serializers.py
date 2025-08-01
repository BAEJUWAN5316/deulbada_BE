# users/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
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
