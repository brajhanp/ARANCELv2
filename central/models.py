from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos_arancel = models.BooleanField(default=False, help_text="Puede ver y buscar en aranceles")
    permisos_admin = models.BooleanField(default=False, help_text="Puede acceder al panel de administración")
    permisos_usuarios = models.BooleanField(default=False, help_text="Puede gestionar usuarios y roles")
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre if self.rol else 'Sin rol'}"

class HistorialBusqueda(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    tipo_resultado = models.CharField(max_length=50, blank=True, null=True)  # Sección, Capítulo, Partida, Subpartida
    id_resultado = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_busqueda']
        verbose_name = 'Historial de Búsqueda'
        verbose_name_plural = 'Historiales de Búsqueda'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.termino_busqueda} ({self.fecha_busqueda.strftime('%d/%m/%Y %H:%M')})"


class Reporte(models.Model):
    """Modelo para registrar operaciones de trazabilidad en clasificación arancelaria"""
    TIPO_ACCION_CHOICES = [
        ('búsqueda', 'Búsqueda de Código'),
        ('consulta_detalle', 'Consulta de Detalle'),
        ('clasificación', 'Clasificación Realizada'),
        ('modificación', 'Modificación de Clasificación'),
        ('descarga_doc', 'Descarga de Documento'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes')
    fecha_operacion = models.DateTimeField(auto_now_add=True, db_index=True)
    codigo_arancelario = models.CharField(max_length=13, blank=True, null=True, db_index=True)
    descripcion_clasificacion = models.TextField(blank=True, null=True)
    tipo_accion = models.CharField(max_length=50, choices=TIPO_ACCION_CHOICES, db_index=True)
    resultado_operacion = models.CharField(max_length=50, choices=[
        ('exitosa', 'Exitosa'),
        ('con_advertencia', 'Con Advertencia'),
        ('rechazada', 'Rechazada'),
        ('pendiente', 'Pendiente'),
    ], default='exitosa')
    detalles_adicionales = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_operacion']
        verbose_name = 'Reporte de Trazabilidad'
        verbose_name_plural = 'Reportes de Trazabilidad'
        indexes = [
            models.Index(fields=['usuario', '-fecha_operacion']),
            models.Index(fields=['codigo_arancelario', '-fecha_operacion']),
            models.Index(fields=['tipo_accion', '-fecha_operacion']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.codigo_arancelario} ({self.fecha_operacion.strftime('%d/%m/%Y %H:%M')})"


class Bitacora(models.Model):
    """Modelo para registrar todas las acciones relevantes de los usuarios (bitácora de auditoría)"""
    TIPO_ACCION_CHOICES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('busqueda', 'Búsqueda'),
        ('consulta', 'Consulta de Detalle'),
        ('modificacion', 'Modificación'),
        ('eliminacion', 'Eliminación'),
        ('creacion', 'Creación'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bitacora_entradas')
    fecha_accion = models.DateTimeField(auto_now_add=True, db_index=True)
    tipo_accion = models.CharField(max_length=50, choices=TIPO_ACCION_CHOICES, db_index=True)
    descripcion = models.TextField(help_text="Descripción detallada de la acción")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    detalles_adicionales = models.JSONField(default=dict, blank=True, help_text="Información adicional en formato JSON")
    
    class Meta:
        ordering = ['-fecha_accion']
        verbose_name = 'Entrada de Bitácora'
        verbose_name_plural = 'Bitácora de Auditoría'
        indexes = [
            models.Index(fields=['usuario', '-fecha_accion']),
            models.Index(fields=['tipo_accion', '-fecha_accion']),
            models.Index(fields=['-fecha_accion']),
        ]
    
    def __str__(self):
        usuario_nombre = self.usuario.username if self.usuario else 'Usuario eliminado'
        return f"{usuario_nombre} - {self.get_tipo_accion_display()} ({self.fecha_accion.strftime('%d/%m/%Y %H:%M:%S')})"