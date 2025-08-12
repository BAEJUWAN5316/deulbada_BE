<<<<<<< HEAD
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Value, BooleanField, Q
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Follow, UserProfile
from .serializers import (
    UserSignupSerializer, ProducerSignupSerializer, CustomTokenObtainPairSerializer,
    ProfileSetupSerializer, ProfilePageSerializer,
    ReportSerializer, UserSearchSerializer, search_users,
)
from posts.models import Post

User = get_user_model()

class SmallPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 50

# 가입/로그인
class SignupView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

class ProducerSignupView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProducerSignupSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

# 중복 체크
class EmailCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return Response({"detail":"email 파라미터 필요"}, status=400)
        return Response({"exists": User.objects.filter(email=email).exists()})

class AccountIdCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        account_id = request.GET.get("account_id")
        if not account_id:
            return Response({"detail":"account_id 파라미터 필요"}, status=400)
        return Response({"exists": User.objects.filter(account_id=account_id).exists()})

# 내 프로필
class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        me = (User.objects.filter(pk=request.user.pk)
              .annotate(follower_count=Count("followed_by", distinct=True),
                        following_count=Count("following", distinct=True))
              .first())
        data = ProfilePageSerializer(me, context={"viewer": request.user}).data
        return Response(data)

# 프로필 설정/수정
class ProfileSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request):
        ser = ProfileSetupSerializer(request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
    patch = put

class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request):
        ser = ProfileSetupSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

# 농장주 프로필 작성/수정
class FarmOwnerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request):
        pf, _ = UserProfile.objects.get_or_create(user=request.user)
        for k in ["profile_image","bio","ceo_name","phone","business_number","address_postcode","address_line1","address_line2","business_doc"]:
            if k in request.data:
                setattr(pf, k, request.data[k])
        pf.is_farm_owner = True
        pf.save()
        if not request.user.is_farm_owner:
            request.user.is_farm_owner = True
            request.user.save(update_fields=["is_farm_owner"])
        return Response({"message":"농장주 프로필 저장됨"})
    patch = put

# 상대 프로필 (여긴 이미 is_following 처리 OK)
class ProfileRetrieveView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, account_id):
        target = get_object_or_404(User, account_id=account_id)
        if request.user.is_authenticated:
            qs = User.objects.filter(pk=target.pk).annotate(
                follower_count=Count("followed_by", distinct=True),
                following_count=Count("following", distinct=True),
                is_following=Exists(Follow.objects.filter(follower=request.user, following=OuterRef("pk"))),
            )
        else:
            qs = User.objects.filter(pk=target.pk).annotate(
                follower_count=Count("followed_by", distinct=True),
                following_count=Count("following", distinct=True),
                is_following=Value(False, output_field=BooleanField()),
            )
        obj = qs.first()
        data = ProfilePageSerializer(obj, context={"viewer": request.user if request.user.is_authenticated else None}).data
        return Response(data)

# 팔로워 목록(페이지네이션) — is_following 추가 + 정렬 안전하게
class FollowersListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSearchSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        u = get_object_or_404(User, account_id=self.kwargs["account_id"])
        base_qs = User.objects.filter(following__following=u)
        if self.request.user.is_authenticated:
            return base_qs.annotate(
                is_following=Exists(Follow.objects.filter(
                    follower=self.request.user, following=OuterRef("pk")
                ))
            ).order_by("account_id")
        else:
            return base_qs.annotate(
                is_following=Value(False, output_field=BooleanField())
            ).order_by("account_id")

# 팔로잉 목록(페이지네이션) — is_following 추가 + 정렬 안전하게
class FollowingListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSearchSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        u = get_object_or_404(User, account_id=self.kwargs["account_id"])
        base_qs = User.objects.filter(followed_by__follower=u)
        if self.request.user.is_authenticated:
            return base_qs.annotate(
                is_following=Exists(Follow.objects.filter(
                    follower=self.request.user, following=OuterRef("pk")
                ))
            ).order_by("account_id")
        else:
            return base_qs.annotate(
                is_following=Value(False, output_field=BooleanField())
            ).order_by("account_id")

class FollowToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, account_id):
        target = get_object_or_404(User, account_id=account_id)
        if target == request.user:
            return Response({"detail":"자기 자신은 팔로우 불가"}, status=400)
        obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if created: return Response({"message":"팔로우 완료","is_following":True}, status=201)
        obj.delete(); return Response({"message":"언팔로우 완료","is_following":False})

# 내가 쓴 글 리스트(페이지네이션 + 집계)
class MyPostsView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SmallPagination
    from posts.serializers import PostListSerializer
    serializer_class = PostListSerializer
    def get_queryset(self):
        from django.db.models import Count
        return (Post.objects.filter(author=self.request.user)
                .annotate(like_count=Count("likes", distinct=True), comment_count=Count("comments", distinct=True))
                .order_by("-created_at"))

# 신고
class ReportCreateAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

# 유저 검색(페이지네이션) — is_following 추가 + 정렬 변경
class UserSearchAPIView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSearchSerializer
    pagination_class = SmallPagination
    def get_queryset(self):
        q = self.request.GET.get("q","").strip()
        if not q:
            return User.objects.none()
        base_qs = search_users(q)
        if self.request.user.is_authenticated:
            return base_qs.annotate(
                is_following=Exists(Follow.objects.filter(
                    follower=self.request.user, following=OuterRef("pk")
                ))
            ).order_by("account_id")
        else:
            return base_qs.annotate(
                is_following=Value(False, output_field=BooleanField())
            ).order_by("account_id")
=======
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import (
    UserSerializer,
    ReportSerializer,
    UserDetailSerializer,
    SignupSerializer,
)

# 🔍 유저 검색
class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'account_id']
    permission_classes = [IsAuthenticated]

# 📝 내가 쓴 게시글 조회
class MyPostsView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# 🚨 유저 신고
class ReportCreateAPIView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

# 🆕 회원가입
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "회원가입 성공",
                "user_id": user.id,
                "is_farm_owner": getattr(getattr(user, "profile", None), "is_farm_owner", False),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
>>>>>>> feature/hyoeun
