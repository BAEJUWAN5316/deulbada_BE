from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SignupSerializer
from .models import User

class SignupViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            message = (
                "회원가입 1단계 완료. "
                "사업자 정보를 입력해주세요." if user.role == "producer"
                else "프로필 정보를 입력해주세요."
            )

            return Response({
                "user_id": user.id,
                "role": user.role,
                "message": message
            }, status=status.HTTP_201_CREATED)

        errors = serializer.errors
        if "email" in errors:
            return Response({"error": "이미 사용 중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)
        if "password" in errors:
            return Response({"error": errors["password"][0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_email(request):
    email = request.query_params.get('email')
    if not email:
        return Response({"error": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    exists = User.objects.filter(email=email).exists()
    return Response({"is_taken": exists}, status=status.HTTP_200_OK)
