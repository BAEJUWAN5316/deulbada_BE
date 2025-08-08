# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import FarmerSignupSerializer


class FarmerSignupView(APIView):
    def post(self, request):
        serializer = FarmerSignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user_id": user.id,
                "email": user.email,
                "message": "생산자 회원가입 1단계 완료. 다음 단계로 이동해주세요."
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
