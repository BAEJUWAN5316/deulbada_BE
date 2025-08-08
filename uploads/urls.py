from django.urls import path
from .views import PresignedUrlView

urlpatterns = [
    path('presigned-url/', PresignedUrlView.as_view(), name='presigned-url'),
]
