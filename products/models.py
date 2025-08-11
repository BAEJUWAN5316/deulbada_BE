# products/models.py

from django.db import models
from django.conf import settings

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()
    is_sold = models.BooleanField(default=False)  # ✅ 이게 있어야 에러 안 남
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
