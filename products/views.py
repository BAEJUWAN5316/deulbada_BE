from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied

from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter # ProductFilter might need update too
# from categories.models import Category # Removed
from users.models import User

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter # ProductFilter needs to be updated for new category field
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Product.objects.all()

        # Filter by username from URL path
        username = self.kwargs.get('username')
        if username:
            qs = qs.filter(seller__username=username)

        # Filter by category from URL path
        category_name = self.kwargs.get('category_name')
        if category_name:
            qs = qs.filter(category=category_name)

        return qs

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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