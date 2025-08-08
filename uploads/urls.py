from django.urls import path
from .views import FileUploadView

urlpatterns = [
    path('presigned-url/', FileUploadView.as_view(), name='presigned-url'),
]
