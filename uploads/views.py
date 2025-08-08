import boto3
from botocore.exceptions import ClientError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
import uuid
import os

class FileUploadView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        print("Content-Type:", request.content_type)
        print("FILES:", request.FILES)
        print("DATA:", request.data)
        print("POST:", request.POST)

        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({
                'error': 'No file provided',
                'debug_info': {
                    'content_type': request.content_type,
                    'files_keys': list(request.FILES.keys()),
                    'data_keys': list(request.data.keys()) if hasattr(request, 'data') else []
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response({
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 파일 검증
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return Response({
                'error': 'File too large. Maximum size is 10MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 허용된 파일 타입 검증
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
        if uploaded_file.content_type not in allowed_types:
            return Response({
                'error': 'File type not allowed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # S3 클라이언트 초기화
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # 고유한 파일명 생성
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        object_name = f'uploads/{request.user.id}/{unique_filename}'

        try:
            # S3에 업로드
            s3_client.upload_fileobj(
                uploaded_file,
                settings.AWS_STORAGE_BUCKET_NAME,
                object_name,
                ExtraArgs={
                    'ContentType': uploaded_file.content_type,
                    'ACL': 'public-read'  # 공개 읽기 권한
                }
            )
            
            # 업로드된 파일 URL
            file_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{object_name}'

            return Response({
                'message': 'File uploaded successfully',
                'file_url': file_url,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'object_name': object_name
            }, status=status.HTTP_201_CREATED)

        except ClientError as e:
            return Response({
                'error': f'Upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)