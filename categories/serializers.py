from rest_framework import serializers
from .models import Category

# SubCategorySerializer is no longer needed if hierarchy is removed
# class SubCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'type', 'icon_image', 'parent'] # Parent field removed

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon_image', 'created_at', 'updated_at'] # Removed 'parent', 'subcategories'
        read_only_fields = ['created_at', 'updated_at']