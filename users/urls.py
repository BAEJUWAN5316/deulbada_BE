from django.urls import path
from .views import ReportCreateAPIView

urlpatterns = [
 path('report/', ReportCreateAPIView.as_view(), name='user-report'),
]
