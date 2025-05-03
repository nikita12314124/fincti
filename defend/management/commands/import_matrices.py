from django.core.management.base import BaseCommand, CommandError
from defend.utils import import_d3fend_matrix, import_detection_matrix

class Command(BaseCommand):
    help = 'Импорт D3FEND CAD и/или ATT&CK layer одной командой'

    def add_arguments(self, parser):
        parser.add_argument('--d3fend-json', type=str, help='Путь до bushwalk.json')
        parser.add_argument('--name-d3fend', type=str)
        parser.add_argument('--desc-d3fend', type=str, default='')
        parser.add_argument('--detect-file', type=str, help='Путь до CSV/JSON layer')
        parser.add_argument('--source', type=str, help='Имя TelemetrySource')
        parser.add_argument('--name-detect', type=str)
        parser.add_argument('--desc-detect', type=str, default='')

    def handle(self, *args, **opts):
        if not opts['d3fend_json'] and not opts['detect_file']:
            raise CommandError("Укажите хотя бы --d3fend-json или --detect-file")
        if opts['d3fend_json']:
            m = import_d3fend_matrix(
                opts['d3fend_json'],
                opts['name_d3fend'] or opts['d3fend_json'],
                opts['desc_d3fend']
            )
            self.stdout.write(f"✅ D3FEND matrix '{m.name}' imported")
        if opts['detect_file']:
            if not opts['source']:
                raise CommandError("--source обязательно при --detect-file")
            m = import_detection_matrix(
                opts['detect_file'],
                opts['source'],
                opts['name_detect'] or opts['detect_file'],
                opts['desc_detect']
            )
            self.stdout.write(f"✅ Detection matrix '{m.name}' imported")
