from django.db import models
from core.models.base import TimeStampedModel
from django.core.exceptions import ValidationError

class Category(TimeStampedModel):
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
        '건어물류', '젓갈류', '어패가공품', '기타수산물',
    ]

    ALL_CATEGORIES = []
    for cat in AGRICULTURAL_CATEGORIES + FISHING_CATEGORIES:
        ALL_CATEGORIES.append((cat, cat)) # Create (value, display_name) tuples

    name = models.CharField(max_length=100, unique=True, choices=ALL_CATEGORIES) # Use choices
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    icon_image = models.URLField(blank=True, null=True)
    # parent field removed

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
