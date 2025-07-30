from rest_framework import generics, status
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


#전체 사용자 리스트 API (테스트/관리자용)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# 프로필 설정 API (회원가입 2단계)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "프로필 설정 완료!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
