from rest_framework import serializers
from .models import Product, Tag
from categories.models import Category

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source='seller.username')
    is_seller_verified = serializers.SerializerMethodField()
    
    # Flattened category fields for response
    category_type = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    # Write-only field for setting category by ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False
    )
    
    tags = serializers.StringRelatedField(many=True, read_only=True)
    tag_input = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="쉼표로 구분된 태그 문자열을 입력하세요.")

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_username', 'is_seller_verified', 'name', 'description', 'price',
            'image_urls', 'variety', 'region', 'harvest_date', 'created_at', 'updated_at',
            'category_type', 'category_name', 'category_id', 'tags', 'tag_input'
        ]
        read_only_fields = ['seller', 'created_at']

    def get_category_type(self, obj):
        if obj.category:
            return obj.category.get_type_display()
        return None

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def get_is_seller_verified(self, obj):
        try:
            return obj.seller.profile.is_farm_verified
        except AttributeError:
            return False

    def _handle_tags(self, product, tag_input):
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
    # Write-only field for setting category by ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False
    )
    tags = serializers.StringRelatedField(many=True, read_only=True)
    tag_input = serializers.CharField(required=False, allow_blank=True, help_text="쉼표로 구분된 태그 문자열을 입력하세요.")

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'image_urls', 'variety', 'region',
            'harvest_date', 'category_id', 'tags', 'tag_input'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tag_input'] = ', '.join(tag.name for tag in instance.tags.all())
        # Add flattened category fields to the response representation
        if instance.category:
            representation['category_type'] = instance.category.get_type_display()
            representation['category_name'] = instance.category.name
        else:
            representation['category_type'] = None
            representation['category_name'] = None
        return representation

    def _handle_tags(self, product, tag_input):
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

