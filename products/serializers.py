from rest_framework import serializers
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

from rest_framework import serializers
from .models import Product, ProductCategory
from categories.models import Category

class ProductCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = ProductCategory
        fields = ['category', 'category_name']
        read_only_fields = ['category_name']

class ProductSerializer(serializers.ModelSerializer):
    product_categories = ProductCategorySerializer(many=True, read_only=True)
    seller_username = serializers.ReadOnlyField(source='seller.username')
    is_seller_verified = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField() # 카테고리 이름을 가져오기 위한 필드 추가

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_username', 'is_seller_verified', 'name', 'description', 'price', 'stock',
            'image_urls', 'variety', 'region', 'harvest_date', 'created_at', 'updated_at',
            'product_categories', 'categories' # categories 필드 추가
        ]
        read_only_fields = ['seller', 'created_at']

    def get_is_seller_verified(self, obj):
        try:
            return obj.seller.profile.is_farm_verified
        except AttributeError:
            return False

    def get_categories(self, obj):
        # Product에 연결된 모든 카테고리 이름을 리스트로 반환
        return [pc.category.name for pc in obj.product_categories.all()]

    def validate_image_urls(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5장까지 업로드할 수 있습니다.")
        return value

    def create(self, validated_data):
        # 현재 요청을 보낸 사용자를 판매자로 설정
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

