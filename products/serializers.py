from rest_framework import serializers
from .models import Product, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source='seller.username')
    is_seller_verified = serializers.SerializerMethodField()
    
    # 응답에는 태그 이름의 리스트를 포함
    tags = serializers.StringRelatedField(many=True, read_only=True)
    # 입력을 받을 때는 쉼표로 구분된 문자열을 사용
    tag_input = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="쉼표로 구분된 태그 문자열을 입력하세요.")

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_username', 'is_seller_verified', 'name', 'description', 'price',
            'image_urls', 'variety', 'region', 'harvest_date', 'created_at', 'updated_at',
            'category', 'tags', 'tag_input' # 'tags'는 읽기용, 'tag_input'은 쓰기용
        ]
        read_only_fields = ['seller', 'created_at']

    def get_is_seller_verified(self, obj):
        try:
            return obj.seller.profile.is_farm_verified
        except AttributeError:
            return False

    def validate_image_urls(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5장까지 업로드할 수 있습니다.")
        return value

    def _handle_tags(self, product, tag_input):
        """Helper function to process the tag string and update the product's tags."""
        product.tags.clear()
        if tag_input:
            tag_names = [name.strip() for name in tag_input.split(',') if name.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                product.tags.add(tag)

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        tag_input = validated_data.pop('tag_input', None)
        product = super().create(validated_data)
        if tag_input is not None:
            self._handle_tags(product, tag_input)
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    # 응답에는 태그 이름의 리스트를 포함
    tags = serializers.StringRelatedField(many=True, read_only=True)
    # 입력을 받을 때는 쉼표로 구분된 문자열을 사용
    tag_input = serializers.CharField(required=False, allow_blank=True, help_text="쉼표로 구분된 태그 문자열을 입력하세요.")

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'image_urls', 'variety', 'region',
            'harvest_date', 'category', 'tags', 'tag_input'
        ]

    def validate_image_urls(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5장까지 업로드할 수 있습니다.")
        return value

    def to_representation(self, instance):
        """On response, populate tag_input with the current comma-separated tags."""
        representation = super().to_representation(instance)
        representation['tag_input'] = ', '.join(tag.name for tag in instance.tags.all())
        return representation

    def _handle_tags(self, product, tag_input):
        """Helper function to process the tag string and update the product's tags."""
        if tag_input:
            tag_names = [name.strip() for name in tag_input.split(',') if name.strip()]
            tags_to_set = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tags_to_set.append(tag)
            product.tags.set(tags_to_set)
        else:
            product.tags.clear()

    def update(self, instance, validated_data):
        tag_input = validated_data.pop('tag_input', None)
        instance = super().update(instance, validated_data)
        
        if tag_input is not None:
            self._handle_tags(instance, tag_input)
            
        return instance

