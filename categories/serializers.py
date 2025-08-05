from rest_framework import serializers
from .models import Category

class SubCategorySerializer(serializers.ModelSerializer):
    """하위 카테고리 직렬화를 위한 시리얼라이저"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon_image', 'parent']

class CategorySerializer(serializers.ModelSerializer):
    """최상위 카테고리 및 하위 카테고리 직렬화를 위한 시리얼라이저"""
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon_image', 'parent', 'subcategories']
