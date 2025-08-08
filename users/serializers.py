from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_farm_owner = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ["email", "password", "is_farm_owner"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
