from rest_framework import serializers
from .models import Product
# from .models import ProductCategory # Removed
# from categories.models import Category # Removed

# ProductCategorySerializer is removed
# class ProductCategorySerializer(serializers.ModelSerializer):
#     category_name = serializers.ReadOnlyField(source='category.name')
#
#     class Meta:
#         model = ProductCategory
#         fields = ['category', 'category_name']
#         read_only_fields = ['category_name']

class ProductSerializer(serializers.ModelSerializer):
    # product_categories = ProductCategorySerializer(many=True, read_only=True) # Removed
    seller_username = serializers.ReadOnlyField(source='seller.username')
    is_seller_verified = serializers.SerializerMethodField()
    # categories = serializers.SerializerMethodField() # Removed, as category is now a direct field

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_username', 'is_seller_verified', 'name', 'description', 'price',
            'image_urls', 'variety', 'region', 'harvest_date', 'created_at', 'updated_at',
            'category' # Direct category field
        ]
        read_only_fields = ['seller', 'created_at']

    def get_is_seller_verified(self, obj):
        try:
            return obj.seller.profile.is_farm_verified
        except AttributeError:
            return False

    # get_categories method is removed
    # def get_categories(self, obj):
    #     return [pc.category.name for pc in obj.product_categories.all()]

    def validate_image_urls(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5장까지 업로드할 수 있습니다.")
        return value

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)
