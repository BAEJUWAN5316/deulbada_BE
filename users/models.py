from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profile_image = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', '처리 대기'),
        ('resolved', '처리 완료'),
        ('rejected', '무시됨'),
    ]

    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports_made'
    )
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports_received'
    )
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # ✅ 추가
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'target_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reporter.username} → {self.target_user.username} ({self.status})"

# 자동 정지 기능 – 유저가 신고 3회 이상이면 정지
def check_auto_ban(user):
    report_count = Report.objects.filter(target_user=user, status='pending').count()
    if report_count >= 3 and user.is_active:
        user.is_active = False  # 유저 정지
        user.save()
