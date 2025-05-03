from django.contrib import admin
from .models import Region, Sector, TelemetrySource, APTGroup, Technique, Procedure

admin.site.register(Region)
admin.site.register(Sector)
admin.site.register(TelemetrySource)
admin.site.register(APTGroup)
admin.site.register(Technique)
admin.site.register(Procedure)
