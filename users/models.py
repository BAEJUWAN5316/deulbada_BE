from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# 유저 매니저
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


# 사용자 모델
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_farmer = models.BooleanField(default=False)
    is_profile_completed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


# 업로드 경로 지정
def business_license_upload_path(instance, filename):
    return f'business_licenses/{instance.user.id}/{filename}'


# 농장주 프로필
class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')

    representative_name = models.CharField("대표자명", max_length=100)
    contact = models.CharField("연락처", max_length=20)
    business_number = models.CharField("사업자 등록번호", max_length=30)
    address = models.CharField("주소", max_length=255)
    address_detail = models.CharField("상세주소", max_length=255)
    business_type = models.CharField("업태", max_length=100)

    registration_image = models.ImageField(  # 여기! 사진 등록은 ImageField
        "사업자등록증 이미지",
        upload_to=business_license_upload_path,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}의 농장주 프로필"
