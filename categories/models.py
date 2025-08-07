from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from core.models.base import TimeStampedModel
from django.core.exceptions import ValidationError

class Category(MPTTModel, TimeStampedModel):
    TYPE_CHOICES = (
        ('agricultural', '농산물'),
        ('fishing', '수산물'),
    )

    AGRICULTURAL_CATEGORIES = [
        '잎채소류', '열매채소류', '뿌리채소류', '과일류',
        '곡류·잡곡', '버섯류', '견과류', '기타농산물',
    ]
    FISHING_CATEGORIES = [
        '생선류', '갑각류', '조개류', '연체류',
        '건어물류', '젓갈류', '어패가공품', '기타 수산물',
    ]

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    icon_image = models.URLField(blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "Categories"

    def clean(self):
        super().clean()
        if self.type == 'agricultural' and self.name not in self.AGRICULTURAL_CATEGORIES:
            raise ValidationError(f"'{self.name}'은(는) 농산물 카테고리에 속하지 않습니다.")
        if self.type == 'fishing' and self.name not in self.FISHING_CATEGORIES:
            raise ValidationError(f"'{self.name}'은(는) 수산물 카테고리에 속하지 않습니다.")

    def __str__(self):
        return self.name