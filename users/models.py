from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ✅ 커스텀 User 매니저
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

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser는 is_staff=True 여야 합니다.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser는 is_superuser=True 여야 합니다.')

        return self.create_user(account_id, email, password, **extra_fields)

# ✅ 커스텀 User 모델
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

# ✅ UserProfile 모델
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.URLField(blank=True, null=True)  # ✅ null=True 포함
    bio = models.TextField(blank=True, null=True)
    is_farm_owner = models.BooleanField(default=False)
    is_farm_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.account_id}의 프로필"

# ✅ Follow 모델
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')   # 내가 팔로우하는 사람들
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')  # 나를 팔로우한 사람들
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.account_id} → {self.following.account_id}"
