from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.conf import settings

from defend.models import (
    DefendMatrix,
    DetectionMatrix,
    DefendCoverageEntry,
    DetectionCoverageEntry
)
from cti.models import Procedure

class Command(BaseCommand):
    help = 'Приоритизационный анализ процедур по матрицам, секторам, регионам и источникам'

    def add_arguments(self, parser):
        parser.add_argument('--sector', action='append', required=False,
                            help='Имя сектора (можно указать несколько раз)')
        parser.add_argument('--region', action='append', required=False,
                            help='Имя региона (можно указать несколько раз)')
        parser.add_argument('--sources', action='append', required=False,
                            help='Имя TelemetrySource (можно указать несколько раз)')
        parser.add_argument('--detect-matrix', type=str, required=False,
                            help='Имя DetectionMatrix для анализа')
        parser.add_argument('--defend-matrix', type=str, required=False,
                            help='Имя DefendMatrix для анализа')

    def handle(self, *args, **options):
        sectors     = options.get('sector') or []
        regions     = options.get('region') or []
        sources     = options.get('sources') or []
        detect_name = options.get('detect_matrix')
        defend_name = options.get('defend_matrix')

        # Загружаем матрицы из БД
        dmat = DetectionMatrix.objects.get(name=detect_name) if detect_name else None
        fmat = DefendMatrix.objects.get(name=defend_name)   if defend_name else None

        # Базовый queryset процедур
        qs = Procedure.objects.select_related('group','technique')
        if sectors:
            qs = qs.filter(group__sectors__name__in=sectors).distinct()
        if regions:
            qs = qs.filter(group__regions__name__in=regions).distinct()
        if sources:
            qs = qs.filter(telemetry_sources__name__in=sources).distinct()

        results = []
        for proc in qs:
            tech = proc.technique
            # покрытие детекцией
            d_cov = 0
            if dmat:
                d_cov = (DetectionCoverageEntry.objects
                         .filter(matrix=dmat, technique=tech)
                         .aggregate(Max('coverage'))['coverage__max'] or 0)
            # покрытие защитой
            f_cov = 0
            if fmat:
                f_cov = (DefendCoverageEntry.objects
                         .filter(matrix=fmat, technique=tech)
                         .aggregate(Max('coverage'))['coverage__max'] or 0)

            # вычисляем score
            freq  = proc.frequency
            blind = 1 - max(d_cov, f_cov)
            rare  = proc.rarity
            score = (settings.RISK_WEIGHT_FREQ * freq +
                     settings.RISK_WEIGHT_BLIND * blind +
                     settings.RISK_WEIGHT_RARE * rare)

            if score > 0:
                results.append((proc, d_cov, f_cov, score))

        # сортировка по убыванию score
        results.sort(key=lambda x: x[3], reverse=True)

        # вывод результатов
        for proc, d_cov, f_cov, score in results:
            self.stdout.write(
                f"{proc.group.identifier},{proc.name},{proc.technique.mitre_id},"
                f"detect_cov={d_cov},defend_cov={f_cov},score={score:.2f}"
            )
        self.stdout.write(self.style.SUCCESS(f"Всего процедур: {len(results)}"))

