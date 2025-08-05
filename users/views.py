from rest_framework import generics, permissions
from .models import Report, check_auto_ban  
from .serializers import ReportSerializer

class ReportCreateAPIView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        report = serializer.save(reporter=self.request.user)
        check_auto_ban(report.target_user) 
