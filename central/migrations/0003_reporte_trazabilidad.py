# Generated migration for new Reporte model (trazabilidad)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0002_rol_perfilusuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_operacion', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('codigo_arancelario', models.CharField(blank=True, db_index=True, max_length=13, null=True)),
                ('descripcion_clasificacion', models.TextField(blank=True, null=True)),
                ('tipo_accion', models.CharField(choices=[('búsqueda', 'Búsqueda de Código'), ('consulta_detalle', 'Consulta de Detalle'), ('clasificación', 'Clasificación Realizada'), ('modificación', 'Modificación de Clasificación'), ('descarga_doc', 'Descarga de Documento')], db_index=True, max_length=50)),
                ('resultado_operacion', models.CharField(choices=[('exitosa', 'Exitosa'), ('con_advertencia', 'Con Advertencia'), ('rechazada', 'Rechazada'), ('pendiente', 'Pendiente')], default='exitosa', max_length=50)),
                ('detalles_adicionales', models.TextField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reportes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reporte de Trazabilidad',
                'verbose_name_plural': 'Reportes de Trazabilidad',
                'ordering': ['-fecha_operacion'],
            },
        ),
        migrations.AddIndex(
            model_name='reporte',
            index=models.Index(fields=['usuario', '-fecha_operacion'], name='central_rep_usuario_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='reporte',
            index=models.Index(fields=['codigo_arancelario', '-fecha_operacion'], name='central_rep_codigo_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='reporte',
            index=models.Index(fields=['tipo_accion', '-fecha_operacion'], name='central_rep_accion_fecha_idx'),
        ),
    ]
