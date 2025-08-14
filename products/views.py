from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied

from .models import Product, Tag
from .serializers import ProductSerializer, ProductUpdateSerializer, TagSerializer
from .filters import ProductFilter
from users.models import User

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Product.objects.all()

        # Filter by account_id from URL path
        account_id = self.kwargs.get('account_id')
        if account_id:
            qs = qs.filter(seller__account_id=account_id)

        # Filter by category from URL path
        category_name = self.kwargs.get('category_name')
        if category_name:
            qs = qs.filter(category__name=category_name)

        return qs

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductUpdateSerializer
        return ProductSerializer

    def get_object(self):
        obj = super().get_object()
        if self.request.method not in permissions.SAFE_METHODS:
            if obj.seller != self.request.user:
                raise PermissionDenied("이 상품에 대한 수정/삭제 권한이 없습니다.")
        return obj

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class TagListAPIView(generics.ListAPIView):
    """
    A view to list all available tags.
    """
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
