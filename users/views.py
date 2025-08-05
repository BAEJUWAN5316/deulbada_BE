from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Follow, User
from .serializers import MyProfileSerializer
from rest_framework.generics import ListAPIView
from .serializers import SimpleUserSerializer

# 🔹 프로필 조회 뷰 (필수)
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MyProfileSerializer(request.user)
        return Response(serializer.data)

# 🔹 팔로우 토글 뷰
class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, account_id):
        try:
            target_user = User.objects.get(account_id=account_id)
        except User.DoesNotExist:
            return Response({"error": "유저를 찾을 수 없습니다."}, status=404)

        if target_user == request.user:
            return Response({"error": "자기 자신을 팔로우할 수 없습니다."}, status=400)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)

        if created:
            return Response({"message": "팔로우 완료"}, status=201)
        else:
            follow.delete()
            return Response({"message": "언팔로우 완료"}, status=200)

# 🔹 팔로워 목록
class FollowerListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleUserSerializer

    def get_queryset(self):
        user = User.objects.get(account_id=self.kwargs['account_id'])
        return [follow.follower for follow in user.follower_set.all()]

# 🔹 팔로잉 목록
class FollowingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleUserSerializer

    def get_queryset(self):
        user = User.objects.get(account_id=self.kwargs['account_id'])
        return [follow.following for follow in user.following_set.all()]