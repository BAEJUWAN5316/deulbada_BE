from django.urls import path
from products.views import ProductCreateView, ProductDetailView

urlpatterns = [
    path('create', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]

from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<str:filter_by>/', ProductListCreateView.as_view(), name='product-list-filtered'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),
]
