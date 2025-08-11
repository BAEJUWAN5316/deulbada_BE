# apps/social/models.py
from django.conf import settings
from django.db import models
from django.db.models import Q

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',   # 내가 팔로우하는 관계들
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by', # 나를 팔로우하는 사람들
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='uq_follow_follower_following'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='ck_follow_no_self_follow'
            ),
        ]
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['following', 'follower']),
        ]

    def __str__(self):
        return f'{self.follower_id} -> {self.following_id}'
