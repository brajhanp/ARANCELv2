#!/usr/bin/env python
"""
Script para actualizar subpartidas con URLs de permisos según regulaciones Bolivia 2025
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SCMAA.settings')
django.setup()

from arancel.models import Subpartida

# Mapeo de categorías HS que requieren permisos en Bolivia 2025
PERMISOS_BOLIVIA = {
    # SENASAG - Animales vivos (Capítulo 01)
    '01': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso sanitario de importación de animales vivos - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # SENASAG - Carnes y despojos (Capítulo 02)
    '02': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso sanitario de importación de carnes - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # SENASAG - Pescado (Capítulo 03)
    '03': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso sanitario de importación de pescado y productos acuáticos - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # SENASAG - Productos lácteos (Capítulo 04)
    '04': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso sanitario de importación de productos lácteos - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # SENASAG - Productos vegetales (Capítulo 07)
    '07': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso fitosanitario de importación de productos vegetales - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # SENASAG - Semillas y plantas vivas (Capítulo 12)
    '12': {
        'requiere_permiso': True,
        'entidad': 'SENASAG',
        'url': 'https://www.senasag.gob.bo/index.php/tramites-y-servicios/servicios-y-requisitos',
        'detalle': 'Permiso fitosanitario de importación de semillas y plantas - Sistema PATUJÚ: https://cepbweb.senasag.gob.bo/egp/'
    },
    # AGEMED - Medicamentos (Capítulo 30)
    '30': {
        'requiere_permiso': True,
        'entidad': 'AGEMED',
        'url': 'https://www.agemed.gob.bo/',
        'detalle': 'Registro y autorización de medicamentos - AGEMED (Agencia Estatal de Medicamentos y Tecnologías en Salud): https://rep.agemed.gob.bo/medicamentos-liname/index'
    },
    # AGEMED - Productos farmacéuticos (Capítulo 33)
    '33': {
        'requiere_permiso': True,
        'entidad': 'AGEMED',
        'url': 'https://www.agemed.gob.bo/',
        'detalle': 'Registro y autorización de productos farmacéuticos y cosméticos - AGEMED: https://rep.agemed.gob.bo/medicamentos-liname/index'
    },
}

def actualizar_permisos():
    """Actualiza las subpartidas con información de permisos requeridos"""
    total_actualizadas = 0
    for codigo_prefix, info in PERMISOS_BOLIVIA.items():
        # Buscar todas las subpartidas que comienzan con este código
        subpartidas = Subpartida.objects.filter(codigo__startswith=codigo_prefix)

        # Si no hay registros en la BD para esta categoría, no mostramos nada
        if subpartidas.count() == 0:
            continue

        # Actualizamos cada subpartida: garantizamos que los campos coincidan
        for subpartida in subpartidas:
            changed = False

            if not subpartida.requiere_permiso:
                subpartida.requiere_permiso = True
                changed = True

            if subpartida.entidad_permiso != info.get('entidad'):
                subpartida.entidad_permiso = info.get('entidad')
                changed = True

            # Usar la URL directa como detalle para que el template abra el permiso
            url = info.get('url') or info.get('detalle')
            if subpartida.detalle_permiso != url:
                subpartida.detalle_permiso = url
                changed = True

            if changed:
                subpartida.save()
                total_actualizadas += 1
                print(f"✓ {subpartida.codigo} - {subpartida.descripcion[:60]}...")

        print(f"  → Categoría {codigo_prefix}: {subpartidas.count()} subpartidas procesadas")
    
    print(f"\n✓ Total de subpartidas actualizadas: {total_actualizadas}")

if __name__ == '__main__':
    print("=" * 80)
    print("ACTUALIZAR PERMISOS DE IMPORTACIÓN - BOLIVIA 2025")
    print("=" * 80)
    print()
    actualizar_permisos()
    print("\n✓ Proceso completado exitosamente")
