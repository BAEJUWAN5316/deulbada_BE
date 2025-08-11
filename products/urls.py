
from django.urls import path
from products.views import ProductCreateView, ProductDetailView

urlpatterns = [
    path('create', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
