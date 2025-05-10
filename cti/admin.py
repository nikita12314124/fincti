from django.contrib import admin
from .models import (
    Region,
    Sector,
    TelemetrySource,
    APTGroup,
    Technique,
    Procedure,
)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TelemetrySource)
class TelemetrySourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(APTGroup)
class APTGroupAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name')
    search_fields = ('identifier', 'name')
    filter_horizontal = ('regions', 'sectors')

autocomplete_fields = ('technique',)

@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ('mitre_id', 'name')
    search_fields = ('mitre_id', 'name')

@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('group', 'name', 'technique')
    list_filter = ('group', 'technique', 'telemetry_sources')
    filter_horizontal = ('telemetry_sources',)

autocomplete_fields = ('technique', 'group')