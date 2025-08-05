from django.db import models
from core.models.base import TimeStampedModel
from core.constants.enums import CategoryType

class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in CategoryType])
    icon_image = models.URLField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
