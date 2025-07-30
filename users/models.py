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
