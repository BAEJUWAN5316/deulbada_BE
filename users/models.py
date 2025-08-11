from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# 🔸 이미지 크기 5MB 제한 검증 함수
def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("이미지 크기는 5MB를 초과할 수 없습니다.")


# 🔸 기본 프로필 이미지 경로 반환 함수
def get_default_profile_image():
    return "default_images/default_profile.jpg"


# 🔸 사용자 커스텀 매니저
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# 🔸 사용자 모델 정의
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    account_id = models.CharField(max_length=30, unique=True)
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to='profile_images/',
        validators=[validate_image_size],
        default=get_default_profile_image,
        blank=True
    )

    is_profile_completed = models.BooleanField(default=False)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Q

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user.save(using=self._db)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 비밀번호는 반드시 set_password()로 해싱해야 함
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'account_id'
    REQUIRED_FIELDS = ['email', 'username']

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}의 프로필"

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
class User(AbstractUser):
    nickname = models.CharField(max_length=30, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    introduction = models.TextField(blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followings', blank=True)

    def __str__(self):
        return f'{self.reporter} → {self.target_user}'
    
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
        return self.nickname or self.username
