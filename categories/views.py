from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(parent__isnull=True) # 최상위 카테고리만 조회
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # 모든 사용자가 조회 가능

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser] # 관리자만 생성/수정/삭제 가능

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser] # 관리자만 생성/수정/삭제 가능