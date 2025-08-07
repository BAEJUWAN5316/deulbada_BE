from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, account_id, email, password=None, **extra_fields):
        if not account_id:
            raise ValueError('account_id는 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(account_id=account_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, account_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(account_id, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    account_id = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'account_id'
    REQUIRED_FIELDS = ['email', 'username']

    objects = UserManager()

    def __str__(self):
        return self.account_id

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.account_id}의 프로필"

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', '처리 대기'),
        ('resolved', '처리 완료'),
        ('rejected', '무시됨'),
    ]
    reporter = models.ForeignKey(User, related_name='reports_made', on_delete=models.CASCADE)
    target_user = models.ForeignKey(User, related_name='reports_received', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reporter} → {self.target_user}'