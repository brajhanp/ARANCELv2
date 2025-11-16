"""
Comando para crear reportes de prueba en la base de datos.
Uso: python manage.py crear_reportes_prueba
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from central.models import Reporte


class Command(BaseCommand):
    help = 'Crea reportes de prueba para demostrar la funcionalidad de trazabilidad'

    def handle(self, *args, **options):
        # Datos de prueba para los reportes
        codigos_prueba = [
            ('8504.10.20', 'Transformadores eléctricos de potencia ≤ 1 kVA'),
            ('6204.62.20', 'Camisetas de algodón para hombre'),
            ('7320.90.00', 'Muelles y ballenas de metal para colchones'),
            ('2106.90.99', 'Preparaciones alimenticias diversas'),
            ('4407.99.90', 'Madera aserrada o desbastada'),
        ]
        
        acciones = [
            ('búsqueda', 'Búsqueda de Código'),
            ('consulta_detalle', 'Consulta de Detalle'),
            ('clasificación', 'Clasificación Realizada'),
        ]
        
        resultados = [
            ('exitosa', 'Exitosa'),
            ('con_advertencia', 'Con Advertencia'),
            ('pendiente', 'Pendiente'),
        ]
        
        # Obtener o crear usuario de prueba
        usuario, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema'
            }
        )
        
        # Crear reportes de prueba
        reportes_creados = 0
        ahora = timezone.now()
        
        for i in range(15):  # Crear 15 reportes de prueba
            codigo, descripcion = codigos_prueba[i % len(codigos_prueba)]
            accion = acciones[i % len(acciones)][0]
            resultado = resultados[i % len(resultados)][0]
            
            # Variar las fechas en los últimos 7 días
            fecha_operacion = ahora - timedelta(days=i % 7, hours=i % 24)
            
            reporte = Reporte.objects.create(
                usuario=usuario,
                codigo_arancelario=codigo,
                descripcion_clasificacion=descripcion,
                tipo_accion=accion,
                resultado_operacion=resultado,
                detalles_adicionales=f'Reporte de prueba #{i+1} - Generado automáticamente'
            )
            
            # Actualizar la fecha (ya que auto_now_add la sobrescribe)
            reporte.fecha_operacion = fecha_operacion
            reporte.save()
            
            reportes_creados += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Se crearon exitosamente {reportes_creados} reportes de prueba'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Accede a http://localhost:8000/central/reportes/ para verlos'
            )
        )
