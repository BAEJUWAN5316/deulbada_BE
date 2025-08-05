# users/serializers.py
from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.ReadOnlyField(source='reporter.id')

    class Meta:
        model = Report
        fields = ['id', 'reporter', 'target_user', 'reason', 'created_at']
        read_only_fields = ['id', 'reporter', 'created_at']

    def validate(self, data):
        reporter = self.context['request'].user
        target = data['target_user']
        if reporter == target:
            raise serializers.ValidationError("자기 자신을 신고할 수 없습니다.")
        if Report.objects.filter(reporter=reporter, target_user=target).exists():
            raise serializers.ValidationError("이미 신고한 유저입니다.")
        return data
