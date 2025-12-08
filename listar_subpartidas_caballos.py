import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SCMAA.settings')
import django
django.setup()

from arancel.models import Subpartida

caballos_subpartidas = list(Subpartida.objects.filter(codigo__icontains='CABALLOS').values_list('codigo', flat=True))

with open('subpartidas_caballos.txt', 'w', encoding='utf-8') as f:
    for codigo in caballos_subpartidas:
        f.write(f'{codigo}\n')

print(f'Se listaron {len(caballos_subpartidas)} subpartidas en subpartidas_caballos.txt') 