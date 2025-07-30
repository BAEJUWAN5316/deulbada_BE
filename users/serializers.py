from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'account_id', 'bio']

    def validate_username(self, value):
        if not (2 <= len(value) <= 10):
            raise serializers.ValidationError("사용자 이름은 2자 이상 10자 이하이어야 합니다.")
        return value

    def validate_account_id(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("영문, 숫자, 밑줄(_)만 사용할 수 있습니다.")
        if User.objects.exclude(pk=self.instance.pk).filter(account_id=value).exists():
            raise serializers.ValidationError("이미 사용 중인 ID입니다.")
        return value