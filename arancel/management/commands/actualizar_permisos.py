from django.core.management.base import BaseCommand
from django.db import transaction

from arancel.models import Subpartida


class Command(BaseCommand):
    help = 'Añade enlace de VUCE a subpartidas tipo C y C-CITES; limpia permisos en otros tipos.'

    def handle(self, *args, **options):
        vuce = 'https://www.vuce.gob.bo'

        with transaction.atomic():
            # Añadir VUCE a C y C-CITES
            qs = Subpartida.objects.filter(tipo_de_doc__in=['C', 'C-CITES'])
            updated_add = 0
            for s in qs:
                detalle = (s.detalle_permiso or '').strip()
                if 'vuce.gob.bo' not in detalle:
                    if detalle:
                        detalle = detalle.rstrip() + ' | ' + vuce
                    else:
                        detalle = vuce
                    s.detalle_permiso = detalle
                    # Si no existe entidad_permiso pero tipo C es SENASAG, dejar entidad existente
                    # No sobreescribimos entidad_permiso salvo que esté vacío
                    if not s.entidad_permiso and s.tipo_de_doc == 'C':
                        s.entidad_permiso = 'SENASAG'
                    if not s.entidad_permiso and s.tipo_de_doc == 'C-CITES':
                        s.entidad_permiso = s.entidad_permiso or 'MDRYT (SENASAG) y MMAYA (VMABCCGDF)'
                    s.save()
                    updated_add += 1

            # Limpiar permisos en otros tipos
            other_qs = Subpartida.objects.exclude(tipo_de_doc__in=['C', 'C-CITES'])
            # Actualizar en bloque: dejar campos en blanco / no aplica
            cnt_other = other_qs.update(entidad_permiso='', detalle_permiso='', requiere_permiso=False, estado_permiso='no_aplica')

        self.stdout.write(self.style.SUCCESS(f'VUCE añadido a {updated_add} subpartidas C/C-CITES.'))
        self.stdout.write(self.style.SUCCESS(f'Permisos limpiados en {cnt_other} subpartidas de otros tipos.'))
