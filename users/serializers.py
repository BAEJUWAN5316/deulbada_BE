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
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'account_id', 'username', 'profile_image']
