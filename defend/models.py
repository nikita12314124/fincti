from django.db import models
from cti.models import Technique, TelemetrySource

class DefendMatrix(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

class DefendCoverageEntry(models.Model):
    matrix           = models.ForeignKey(DefendMatrix,   on_delete=models.CASCADE, related_name='coverage_entries')
    technique        = models.ForeignKey(Technique,      on_delete=models.CASCADE, related_name='defend_entries')
    telemetry_source = models.ForeignKey(TelemetrySource,on_delete=models.CASCADE, related_name='defend_entries')
    coverage         = models.FloatField(default=1.0)

class DetectionMatrix(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

class DetectionCoverageEntry(models.Model):
    matrix           = models.ForeignKey(DetectionMatrix,on_delete=models.CASCADE, related_name='entries')
    technique        = models.ForeignKey(Technique,      on_delete=models.CASCADE, related_name='detection_entries')
    telemetry_source = models.ForeignKey(TelemetrySource,on_delete=models.CASCADE, related_name='detection_entries')
    coverage         = models.FloatField()
