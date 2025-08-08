from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSignupSerializer


class SignupView(APIView):
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
