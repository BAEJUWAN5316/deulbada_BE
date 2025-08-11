import re
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q, Count, Exists, OuterRef
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile, Report, Follow
from posts.models import Post

User = get_user_model()
MAX_IMG = 5 * 1024 * 1024

# ====== 추가: 유저 직렬화기들 ======
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "account_id", "username", "profile_image"]

class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(read_only=True, required=False)
    following_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "account_id", "username", "nickname",
            "profile_image", "introduction",
            "is_farm_owner", "is_farm_verified",
            "follower_count", "following_count",
        ]
# =================================

# 회원가입
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "account_id", "username"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, v):
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return v

    def validate_password(self, v):
        if len(v) < 8: raise serializers.ValidationError("비밀번호는 최소 8자 이상.")
        if not re.search(r"[A-Za-z]", v): raise serializers.ValidationError("영문자 포함 필수.")
        if not re.search(r"\d", v):       raise serializers.ValidationError("숫자 포함 필수.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v): raise serializers.ValidationError("특수문자 포함 필수.")
        return v

    def validate_account_id(self, v):
        if v and User.objects.filter(account_id=v).exists():
            raise serializers.ValidationError("이미 사용 중인 ID입니다.")
        return v

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# 생산자(농장주) 회원가입
class ProducerSignupSerializer(UserSignupSerializer):
    ceo_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    business_number = serializers.CharField(write_only=True)
    address_postcode = serializers.CharField(write_only=True)
    address_line1 = serializers.CharField(write_only=True)
    address_line2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    business_doc = serializers.FileField(write_only=True, required=False)

    class Meta(UserSignupSerializer.Meta):
        fields = UserSignupSerializer.Meta.fields + [
            "ceo_name","phone","business_number","address_postcode","address_line1","address_line2","business_doc"
        ]

    def validate(self, attrs):
        for k in ["ceo_name","phone","business_number","address_postcode","address_line1"]:
            if not attrs.get(k):
                raise serializers.ValidationError({k:"필수입력입니다."})
        return attrs

    def create(self, validated_data):
        pf = {k: validated_data.pop(k, None) for k in [
            "ceo_name","phone","business_number","address_postcode","address_line1","address_line2","business_doc"
        ]}
        user = super().create(validated_data)
        user.is_farm_owner = True
        user.save(update_fields=["is_farm_owner"])

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_farm_owner = True
        profile.is_farm_verified = False
        for k, v in pf.items():
            if v is not None: setattr(profile, k, v)
        profile.save()
        return user

# 프로필 초기 설정/수정
class ProfileSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","account_id","introduction","profile_image"]

    def validate_account_id(self, value):
        qs = User.objects.filter(account_id=value)
        if self.instance: qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("이미 사용 중인 ID입니다.")
        return value

    def validate_profile_image(self, img):
        if img and hasattr(img, "size") and img.size > MAX_IMG:
            raise serializers.ValidationError("이미지 5MB 이하만 업로드 가능.")
        return img

    def update(self, inst, data):
        for f in ["username","account_id","introduction","profile_image"]:
            if f in data: setattr(inst, f, data[f])
        inst.is_profile_completed = True
        inst.save()
        return inst

# 목록/검색용
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","account_id","username","profile_image"]

# 프로필 화면(내/상대 공용)
class ProfilePageSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_me = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id","account_id","username","nickname","profile_image","introduction",
            "is_farm_owner","is_farm_verified","follower_count","following_count",
            "is_me","is_following",
        ]

    def get_is_me(self, obj):
        viewer = self.context.get("viewer")
        return bool(viewer and viewer.id == obj.id)

    def get_is_following(self, obj):
        return bool(getattr(obj, "is_following", False))

# 내가 쓴 글 리스트 응답용(포스트 시리얼라이저는 posts 앱에서)
class UserPostSummarySerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ["id","title","content","created_at","like_count","comment_count"]

# 신고
class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Report
        fields = "__all__"

# 검색 쿼리셋
def search_users(q: str):
    return User.objects.filter(Q(username__icontains=q) | Q(account_id__icontains=q))

# 로그인(JWT 커스텀)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # 이메일로 로그인할 거라면 이거 필수
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        pw = attrs.get("password")
        user = authenticate(request=self.context.get("request"), email=email, password=pw)
        if not user:
            raise serializers.ValidationError({"detail":"이메일 또는 비밀번호가 잘못되었습니다."})
        data = super().validate(attrs)
        data.update({"user_id": self.user.id, "email": self.user.email, "message": "로그인 성공"})
        return data
