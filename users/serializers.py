from rest_framework import serializers
from .models import Follow, User

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.ReadOnlyField(source='follower.account_id')
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='account_id'
    )

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'created_at']

    def validate(self, data):
        follower = self.context['request'].user
        following = data['following']

        if follower == following:
            raise serializers.ValidationError("자기 자신을 팔로우할 수 없습니다.")

        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("이미 팔로우 중입니다.")

        return data
