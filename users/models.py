from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


def validate_image_size(image):
    """이미지 5MB 제한"""
    max_size = 5 * 1024 * 1024
    if image and hasattr(image, "size") and image.size > max_size:
        raise ValidationError("이미지 크기는 5MB를 초과할 수 없습니다.")


def get_default_profile_image():
    return "default_images/default_profile.jpg"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("슈퍼유저는 is_staff=True 여야 합니다.")
        if extra.get("is_superuser") is not True:
            raise ValueError("슈퍼유저는 is_superuser=True 여야 합니다.")
        if not password:
            raise ValueError("슈퍼유저 비밀번호는 필수입니다.")
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    # 기본 계정 정보
    email = models.EmailField(unique=True)

    
    account_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    username = models.CharField(max_length=30, unique=False, null=True, blank=True)  
    nickname = models.CharField(max_length=30, blank=True, null=True)
    introduction = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to="profile_images/",
        validators=[validate_image_size],
        default=get_default_profile_image,
        blank=True,
    )

    # 상태/플래그
    is_profile_completed = models.BooleanField(default=False)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 타임스탬프
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 인증 필드 설정(이메일 로그인)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["account_id"]  

    objects = UserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True, null=True,
        validators=[validate_image_size]
    )
    bio = models.TextField(blank=True, null=True)

    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)

    ceo_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    business_number = models.CharField(max_length=50, blank=True)

    address_postcode = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)

    business_doc = models.FileField(upload_to="business_docs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}의 프로필"


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="uq_follow_follower_following",
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="ck_follow_no_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "following"]),
            models.Index(fields=["following", "follower"]),
        ]

    def __str__(self):
        return f"{self.follower_id} -> {self.following_id}"


class Report(models.Model):
    STATUS_CHOICES = [
        ("pending", "처리 대기"),
        ("resolved", "처리 완료"),
        ("rejected", "무시됨"),
    ]
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_made",
        on_delete=models.CASCADE,
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_received",
        on_delete=models.CASCADE,
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporter} → {self.target_user}"



class Report(models.Model):
    STATUS_CHOICES = [
        ("pending", "처리 대기"),
        ("resolved", "처리 완료"),
        ("rejected", "무시됨"),
    ]
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_made",
        on_delete=models.CASCADE,
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_received",
        on_delete=models.CASCADE,
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
<<<<<<< HEAD
        return f"{self.reporter} → {self.target_user}"
=======
        return f'{self.reporter} → {self.target_user}'
>>>>>>> feature/hyoeun
