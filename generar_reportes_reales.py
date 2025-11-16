"""
Script para generar reportes automáticos simulando búsquedas reales.
Uso: python manage.py shell < generar_reportes_reales.py
"""

from django.contrib.auth.models import User
from arancel.models import Subpartida
from central.models import Reporte
from django.utils import timezone

# Obtener el usuario admin (asume que existe)
try:
    usuario = User.objects.get(username='admin')
except User.DoesNotExist:
    # Si no existe, crear uno
    usuario = User.objects.create_user('admin', 'admin@example.com', 'admin')
    print("✓ Usuario 'admin' creado")

# Obtener algunos códigos arancelarios reales
subpartidas = Subpartida.objects.all()[:10]

print(f"\nGenerando reportes automáticos basados en búsquedas reales...")
print(f"Usuario: {usuario.username}")
print(f"Total de subpartidas a procesar: {len(subpartidas)}\n")

reportes_creados = 0
tipo_acciones = ['búsqueda', 'consulta_detalle', 'clasificación']

for i, subpartida in enumerate(subpartidas):
    try:
        reporte = Reporte.objects.create(
            usuario=usuario,
            codigo_arancelario=subpartida.codigo,
            descripcion_clasificacion=subpartida.descripcion[:500],
            tipo_accion=tipo_acciones[i % len(tipo_acciones)],
            resultado_operacion='exitosa',
            detalles_adicionales=f'Búsqueda automática de: {subpartida.codigo}'
        )
        reportes_creados += 1
        print(f"✓ [{i+1}] Reporte creado: {subpartida.codigo} - {subpartida.descripcion[:40]}...")
    except Exception as e:
        print(f"✗ Error al crear reporte para {subpartida.codigo}: {e}")

print(f"\n{'='*60}")
print(f"✓ Se crearon {reportes_creados} reportes automáticos")
print(f"{'='*60}")
print(f"\nVerifica en: http://localhost:8000/central/reportes/")
print(f"Ahora todos los reportes son basados en códigos REALES del sistema\n")
