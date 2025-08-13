from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, TagListAPIView

urlpatterns = [
    path('tags/', TagListAPIView.as_view(), name='tag-list'),
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('category/<str:category_name>/', ProductListCreateView.as_view(), name='product-list-by-category'),
    path('user/<str:username>/', ProductListCreateView.as_view(), name='product-list-by-user'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),
]