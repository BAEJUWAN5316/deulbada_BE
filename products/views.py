from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
# from core.permissions.is_owner import IsOwnerOrReadOnly # IsOwnerOrReadOnly import 제거
from rest_framework.exceptions import PermissionDenied # PermissionDenied import 추가

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 인증된 사용자만 생성 가능, 나머지는 읽기만 가능
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("로그인이 필요합니다.")

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