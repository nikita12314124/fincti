import json
from django.core.management.base import BaseCommand, CommandError
from cti.models import Technique

class Command(BaseCommand):
    help = 'Импорт MITRE ATT&CK техник из STIX JSON (enterprise-attack.json)'

    def add_arguments(self, parser):
        parser.add_argument(
            'stix_path', type=str,
            help='Путь до файла enterprise-attack.json из MITRE ATT&CK'
        )

    def handle(self, *args, **options):
        path = options['stix_path']
        try:
            data = json.load(open(path, encoding='utf-8'))
        except Exception as e:
            raise CommandError(f"Не удалось загрузить STIX JSON: {e}")

        count = 0
        for obj in data.get('objects', []):
            if obj.get('type') == 'attack-pattern':
                # Найти mitre-attack внешнюю ссылку
                external = next(
                    (ref for ref in obj.get('external_references', [])
                     if ref.get('source_name') == 'mitre-attack'),
                    None
                )
                if not external:
                    continue
                tid = external.get('external_id')  # e.g., 'T1566.001'
                name = obj.get('name', '')
                desc = obj.get('description', '')
                tech, created = Technique.objects.get_or_create(
                    mitre_id=tid,
                    defaults={'name': name, 'description': desc}
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Успешно импортировано {count} техник ATT&CK из {path}"
        ))