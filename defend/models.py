from django.db import models


class DefendMatrix(models.Model):
    """
    Пользователь загружает любой D3FEND-JSON – мы даём ему имя.
    """
    name = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # админка
        return self.name


class DetectionMatrix(models.Model):
    """
    Навигатор-heatmap или CSV с покрытием детектов.
    """
    name = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class DefendCell(models.Model):
    """
    Одна процедура «defense-measure» из D3FEND.
    """
    matrix = models.ForeignKey(
        DefendMatrix, related_name="cells", on_delete=models.CASCADE
    )
    d3_id = models.CharField(max_length=32)
    name = models.CharField(max_length=256, blank=True)

    class Meta:
        unique_together = ("matrix", "d3_id")


class DetectCell(models.Model):
    """
    Покрытие техники / процедуры из Detection-heatmap.
    """
    matrix = models.ForeignKey(
        DetectionMatrix, related_name="cells", on_delete=models.CASCADE
    )
    technique_id = models.CharField(max_length=32)
    score = models.FloatField(default=0)

    class Meta:
        unique_together = ("matrix", "technique_id")
