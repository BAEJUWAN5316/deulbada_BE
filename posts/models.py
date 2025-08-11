from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

def validate_image_size(image):
    max_size = 5 * 1024 * 1024
    if image and hasattr(image, "size") and image.size > max_size:
        raise ValidationError("이미지 크기는 5MB를 초과할 수 없습니다.")

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True, validators=[validate_image_size])  # 레거시 1장
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Post {self.id} by {self.author_id}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["post","user"], name="uq_like_post_user")]