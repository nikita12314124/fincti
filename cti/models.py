from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TelemetrySource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class APTGroup(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    regions = models.ManyToManyField(Region, related_name='apt_groups')
    sectors = models.ManyToManyField(Sector, related_name='apt_groups')

    def __str__(self):
        return f"{self.identifier} - {self.name}"

class Technique(models.Model):
    mitre_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.mitre_id} - {self.name}"

class Procedure(models.Model):
    group = models.ForeignKey(
        APTGroup,
        on_delete=models.CASCADE,
        related_name='procedures'
    )
    technique = models.ForeignKey(
        Technique,
        on_delete=models.CASCADE,
        related_name='procedures'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    telemetry_sources = models.ManyToManyField(
        TelemetrySource,
        related_name='procedures'
    )
    frequency = models.FloatField(
        default=0.0,
        help_text='Normalized usage frequency (0.0 - 1.0)'
    )
    rarity = models.FloatField(
        default=0.0,
        help_text='Relative rarity (0.0 - 1.0)'
    )

    def __str__(self):
        return f"{self.group.identifier}: {self.name}"