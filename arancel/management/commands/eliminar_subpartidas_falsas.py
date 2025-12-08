from django.core.management.base import BaseCommand
from arancel.models import Subpartida, Partida

class Command(BaseCommand):
    help = 'Elimina todas las subpartidas cuyo código es igual al de cualquier partida (ignorando mayúsculas y espacios).'

    def handle(self, *args, **options):
        part_codes = [p.codigo.strip().lower() for p in Partida.objects.all()]
        count = 0
        for sub in Subpartida.objects.all():
            if sub.codigo.strip().lower() in part_codes:
                self.stdout.write(self.style.WARNING(f'Eliminando subpartida {sub.codigo} (ID: {sub.id})'))
                sub.delete()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Eliminadas {count} subpartidas cuyo código coincide con el de una partida.')) 