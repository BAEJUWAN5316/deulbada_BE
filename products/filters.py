import django_filters
from .models import Product, ProductCategory

class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(method='filter_by_category')

    class Meta:
        model = Product
        fields = ['category']

    def filter_by_category(self, queryset, name, value):
        # ProductCategory를 통해 특정 category_id를 가진 Product를 필터링합니다.
        return queryset.filter(product_categories__category_id=value).distinct()
