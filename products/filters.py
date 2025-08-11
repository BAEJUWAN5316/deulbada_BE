import django_filters
from .models import Product
# from categories.models import Category # Removed

class ProductFilter(django_filters.FilterSet):
    # category = django_filters.NumberFilter(method='filter_by_category') # Removed

    class Meta:
        model = Product
        fields = ['category'] # Now directly filter by the category field

    # filter_by_category method removed
    # def filter_by_category(self, queryset, name, value):
    #     try:
    #         category = Category.objects.get(id=value)
    #         sub_categories = category.get_descendants(include_self=True)
    #         category_ids = [cat.id for cat in sub_categories]
    #         return queryset.filter(product_categories__category_id__in=category_ids).distinct()
    #     except Category.DoesNotExist:
    #         return queryset.none()