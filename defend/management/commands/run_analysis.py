# defend/management/commands/run_analysis.py
import json
from django.core.management.base import BaseCommand, CommandError
from defend.models import DefendMatrix, DetectionMatrix, DefendCoverageEntry, DetectionCoverageEntry
from cti.models import Procedure
from django.db.models import Max

class Command(BaseCommand):
    help = 'Запуск анализа процедур: фильтрация по матрицам детекции и защиты.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detect-matrix', type=str, help='Имя DetectionMatrix для анализа', required=False
        )
        parser.add_argument(
            '--defend-matrix', type=str, help='Имя DefendMatrix для анализа', required=False
        )

    def handle(self, *args, **options):
        detect_name = options.get('detect_matrix')
        defend_name = options.get('defend_matrix')

        dmat = None
        fmat = None
        if detect_name:
            try:
                dmat = DetectionMatrix.objects.get(name=detect_name)
            except DetectionMatrix.DoesNotExist:
                raise CommandError(f"DetectionMatrix '{detect_name}' не найден.")
        if defend_name:
            try:
                fmat = DefendMatrix.objects.get(name=defend_name)
            except DefendMatrix.DoesNotExist:
                raise CommandError(f"DefendMatrix '{defend_name}' не найден.")

        procedures = Procedure.objects.select_related('group', 'technique').all()
        results = []
        for proc in procedures:
            tid = proc.technique
            # detection coverage
            if dmat:
                d_cov = DetectionCoverageEntry.objects.filter(
                    matrix=dmat, technique=tid
                ).aggregate(Max('coverage'))['coverage__max'] or 0
            else:
                d_cov = None
            # defend coverage
            if fmat:
                f_cov = DefendCoverageEntry.objects.filter(
                    matrix=fmat, technique=tid
                ).aggregate(Max('coverage'))['coverage__max'] or 0
            else:
                f_cov = None
            # apply filtering
            if dmat and not fmat:
                if d_cov == 0:
                    results.append((proc, d_cov, f_cov))
            elif fmat and not dmat:
                if f_cov == 0:
                    results.append((proc, d_cov, f_cov))
            elif dmat and fmat:
                if d_cov == 0 and f_cov == 0:
                    results.append((proc, d_cov, f_cov))
            else:
                raise CommandError('Необходимо указать хотя бы одну матрицу для анализа')

        # Выводим результаты
        for proc, d_cov, f_cov in results:
            self.stdout.write(
                f"{proc.group.identifier},{proc.name}," \
                f"{proc.technique.mitre_id}," \
                f"detect_cov={d_cov},defend_cov={f_cov}"
            )
        self.stdout.write(self.style.SUCCESS(
            f"Всего процедур без покрытия: {len(results)}"
        ))
