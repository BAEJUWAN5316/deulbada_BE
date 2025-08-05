from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon_image', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
