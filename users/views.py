from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import MyProfileSerializer, UserProfileSerializer

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = MyProfileSerializer(user)
        
        # 팔로워/팔로잉 수 임시 값 (Follow 기능 후 연결)
        data = serializer.data
        data['follower_count'] = 0
        data['following_count'] = 0
        return Response(data)

    def put(self, request):
        user = request.user
        profile_data = request.data.get('profile', {})

        user.username = request.data.get('username', user.username)
        user.save()

        serializer = UserProfileSerializer(user.userprofile, data=profile_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "프로필 수정 완료"})
        return Response(serializer.errors, status=400)
