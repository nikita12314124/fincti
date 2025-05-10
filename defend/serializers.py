from rest_framework import serializers
from cti.models import Sector, Region, TelemetrySource
from defend.models import DetectionMatrix, DefendMatrix

class AnalysisInputSerializer(serializers.Serializer):
    sectors        = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    regions        = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    sources        = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    detect_matrix  = serializers.CharField(required=False)
    defend_matrix  = serializers.CharField(required=False)

class ProcedureResultSerializer(serializers.Serializer):
    group          = serializers.CharField()
    procedure      = serializers.CharField()
    technique      = serializers.CharField()
    detect_cov     = serializers.FloatField()
    defend_cov     = serializers.FloatField()
    score          = serializers.FloatField()
