from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

import re
from rest_framework.views import APIView
# apps/social/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from .models import Follow
from .serializers import (
    ProfileSerializer,
    UserSummarySerializer,
    annotated_profile_qs,
)

User = get_user_model()


class ProfileRetrieveView(generics.RetrieveAPIView):
    """
    GET /api/profiles/{account_id}/
    프로필 조회 + follower/following count + is_following
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfileSerializer
    lookup_field = 'account_id'

    def get_queryset(self):
        return annotated_profile_qs(self.request.user)

    # (lookup_field로 account_id 조회)


class FollowersListView(generics.ListAPIView):
    """
    GET /api/profiles/{account_id}/followers/
    해당 유저를 팔로우하는 사람(팔로워) 목록
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSummarySerializer

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        target = get_object_or_404(User, account_id=account_id)

        follower_qs = User.objects.filter(
            following__following=target  # Follow.follower -> User, Follow.following = target
        ).distinct()

        # 목록에도 공통 어노테이션(카운트, is_following) 적용 가능
        return annotated_profile_qs(self.request.user).filter(pk__in=follower_qs.values('pk'))


class FollowingListView(generics.ListAPIView):
    """
    GET /api/profiles/{account_id}/following/
    해당 유저가 팔로우하는 사람(팔로잉) 목록
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSummarySerializer

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        target = get_object_or_404(User, account_id=account_id)

        following_qs = User.objects.filter(
            followed_by__follower=target  # Follow.following -> User, Follow.follower = target
        ).distinct()

        return annotated_profile_qs(self.request.user).filter(pk__in=following_qs.values('pk'))


class FollowToggleView(generics.GenericAPIView):
    """
    POST   /api/profiles/{account_id}/follow/   -> 팔로우 (idempotent)
    DELETE /api/profiles/{account_id}/follow/   -> 언팔로우 (idempotent)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, account_id):
        target = get_object_or_404(User, account_id=account_id)
        if target == request.user:
            return Response({'detail': '자기 자신은 팔로우할 수 없습니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        _, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target
        )
        return Response({'followed': True, 'created': created}, status=status.HTTP_200_OK)

    def delete(self, request, account_id):
        target = get_object_or_404(User, account_id=account_id)
        Follow.objects.filter(
            follower=request.user,
            following=target
        ).delete()
        return Response({'followed': False}, status=status.HTTP_200_OK)

from rest_framework import generics, filters, permissions
from .models import User, Report
from .serializers import UserSerializer, ReportSerializer, UserDetailSerializer
from rest_framework.permissions import IsAuthenticated

# 🔍 유저 검색
class UserSearchAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'account_id']
    permission_classes = [permissions.IsAuthenticated]

# 📝 내가 쓴 게시글 조회
class MyPostsView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# 🚨 유저 신고
class ReportCreateAPIView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
from rest_framework import status

from .serializers import UserSignupSerializer
from users.models import User

# Swagger 문서화를 위한 import
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SignupView(APIView):
    @swagger_auto_schema(
        operation_description="회원가입 1단계 - 이메일과 비밀번호 입력",
        request_body=UserSignupSerializer,
        responses={
            201: openapi.Response(
                description="회원가입 성공",
                examples={
                    "application/json": {
                        "user_id": 1,
                        "email": "user@example.com",
                        "message": "회원가입 1단계 완료. 프로필 정보를 입력해주세요."
                    }
                }
            ),
            400: "잘못된 요청"
        }
    )
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "message": "회원가입 1단계 완료. 프로필 정보를 입력해주세요."
            },
            status=status.HTTP_201_CREATED
        )


class EmailCheckView(APIView):
    @swagger_auto_schema(
        operation_description="이메일 중복 확인 API",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="중복 확인할 이메일 주소",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="사용 가능 여부 응답",
                examples={
                    "application/json": {
                        "available": True,
                        "message": "사용 가능한 이메일입니다."
                    }
                }
            ),
            400: "이메일 누락"
        }
    )
    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response(
                {"message": "이메일을 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"available": False, "message": "이미 사용 중인 이메일입니다."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"available": True, "message": "사용 가능한 이메일입니다."},
                status=status.HTTP_200_OK
            )
