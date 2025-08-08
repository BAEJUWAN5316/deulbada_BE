import boto3
from botocore.client import Config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import os

class PresignedUrlView(APIView):
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능

    def post(self, request, *args, **kwargs):
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type')

        if not file_name or not file_type:
            return Response({'error': 'file_name and file_type are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # S3 클라이언트 초기화
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4')
        )

        # 파일 경로 설정 (예: uploads/user_id/filename.jpg)
        # 실제 사용 시에는 사용자 ID나 다른 고유한 값으로 경로를 구성하는 것이 좋습니다.
        # 여기서는 간단하게 'uploads/' 디렉토리 아래에 저장합니다.
        object_name = f'uploads/{file_name}'

        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': object_name,
                    'ContentType': file_type
                },
                ExpiresIn=300 # 5분 (300초) 동안 유효한 URL
            )
            
            # 최종적으로 S3에 저장될 파일의 공개 URL
            file_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{object_name}'

            return Response({
                'presigned_url': presigned_url,
                'file_url': file_url
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)