import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SCMAA.settings')
import django
django.setup()

from arancel.models import Subpartida

all_subpartidas = list(Subpartida.objects.all().values_list('codigo', flat=True))

# Ruta absoluta al escritorio del usuario
escritorio = os.path.join(os.path.expanduser('~'), 'Desktop', 'subpartidas_todos.txt')

with open(escritorio, 'w', encoding='utf-8') as f:
    for codigo in all_subpartidas:
        f.write(f'{repr(codigo)}\n')

print(f'Se listaron {len(all_subpartidas)} subpartidas en {escritorio}') 