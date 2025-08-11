from django.urls import path
from .views import CategoryListCreateView, CategoryRetrieveUpdateDestroyView # Removed SubCategoryListView

urlpatterns = [
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
    path('<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),
    # path('<int:parent_id>/subcategories/', SubCategoryListView.as_view(), name='subcategory-list'), # Removed
]
