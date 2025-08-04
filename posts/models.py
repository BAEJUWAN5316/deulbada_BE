from django.db import models
from django.contrib.auth import get_user_model  # ✅ 수정: 안전하게 User 가져오기

User = get_user_model()  # ✅ 커스텀 User 지원

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image_urls = models.JSONField(blank=True, null=True)  # 이미지 최대 10장 (예시)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}의 게시글"
