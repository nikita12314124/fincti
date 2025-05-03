from django.contrib import admin
from .models import (
    DefendMatrix, DefendCoverageEntry,
    DetectionMatrix, DetectionCoverageEntry
)

@admin.register(DefendMatrix)
class DefendMatrixAdmin(admin.ModelAdmin):
    list_display = ('name','uploaded_at')

@admin.register(DefendCoverageEntry)
class DefendCoverageEntryAdmin(admin.ModelAdmin):
    list_display = ('matrix','technique','telemetry_source','coverage')

@admin.register(DetectionMatrix)
class DetectionMatrixAdmin(admin.ModelAdmin):
    list_display = ('name','uploaded_at')

@admin.register(DetectionCoverageEntry)
class DetectionCoverageEntryAdmin(admin.ModelAdmin):
    list_display = ('matrix','technique','telemetry_source','coverage')
