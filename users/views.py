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
