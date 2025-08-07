import django_filters
from .models import Product
from categories.models import Category

class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(method='filter_by_category')

    class Meta:
        model = Product
        fields = ['category']

    def filter_by_category(self, queryset, name, value):
        try:
            # 선택된 카테고리 및 모든 하위 카테고리를 가져옴
            category = Category.objects.get(id=value)
            sub_categories = category.get_descendants(include_self=True)
            category_ids = [cat.id for cat in sub_categories]
            return queryset.filter(product_categories__category_id__in=category_ids).distinct()
        except Category.DoesNotExist:
            return queryset.none()
