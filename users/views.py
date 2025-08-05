from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Follow, User
from .serializers import FollowSerializer

# 팔로우 생성
class FollowCreateAPIView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

# 언팔로우 기능
class UnfollowAPIView(generics.DestroyAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        follower = self.request.user
        following_account_id = self.kwargs['account_id']
        try:
            return Follow.objects.get(follower=follower, following__account_id=following_account_id)
        except Follow.DoesNotExist:
            raise NotFound("팔로우하지 않은 유저입니다.")

    def delete(self, request, *args, **kwargs):
        follow = self.get_object()
        follow.delete()
        return Response({'detail': '언팔로우 완료'}, status=status.HTTP_204_NO_CONTENT)

# 팔로워 목록 조회
class FollowerListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        return Follow.objects.filter(following__account_id=account_id)

# 팔로잉 목록 조회
class FollowingListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        return Follow.objects.filter(follower__account_id=account_id)
