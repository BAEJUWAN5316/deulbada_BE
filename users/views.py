import re
from rest_framework.views import APIView
from rest_framework.response import Response
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
