from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all() # No parent__isnull filter needed for flat categories
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

# SubCategoryListView is no longer needed
# class SubCategoryListView(generics.ListAPIView):
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         parent_id = self.kwargs['parent_id']
#         return Category.objects.filter(parent__id=parent_id)