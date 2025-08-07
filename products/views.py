from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from categories.models import Category
from users.models import User
# from core.permissions.is_owner import IsOwnerOrReadOnly # IsOwnerOrReadOnly import 제거
from rest_framework.exceptions import PermissionDenied # PermissionDenied import 추가

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'



class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        filter_by = self.kwargs.get('filter_by')
        if filter_by:
            try:
                # 카테고리 이름으로 필터링
                category = Category.objects.get(name=filter_by)
                return Product.objects.filter(category=category)
            except Category.DoesNotExist:
                # 사용자 이름(username)으로 필터링
                user = get_object_or_404(User, username=filter_by)
                return Product.objects.filter(seller=user)
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 인증된 사용자만 쓰기 가능, 나머지는 읽기만 가능

    def get_object(self):
        obj = super().get_object()
        # 요청 메서드가 쓰기(PUT, PATCH, DELETE)인 경우에만 소유자 확인
        if self.request.method not in permissions.SAFE_METHODS:
            if obj.seller != self.request.user:
                raise PermissionDenied("이 상품에 대한 수정/삭제 권한이 없습니다.")
        return obj