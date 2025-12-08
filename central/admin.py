from django.contrib import admin
from .models import HistorialBusqueda, Rol, PerfilUsuario, Reporte

# Register your models here.
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'permisos_arancel', 'permisos_admin', 'permisos_usuarios']
    list_filter = ['permisos_arancel', 'permisos_admin', 'permisos_usuarios']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'activo', 'fecha_creacion']
    list_filter = ['rol', 'activo', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__email', 'rol__nombre']
    ordering = ['usuario__username']
    raw_id_fields = ['usuario', 'rol']

@admin.register(HistorialBusqueda)
class HistorialBusquedaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'termino_busqueda', 'tipo_resultado', 'fecha_busqueda']
    list_filter = ['tipo_resultado', 'fecha_busqueda', 'usuario']
    search_fields = ['termino_busqueda', 'usuario__username']
    readonly_fields = ['fecha_busqueda']
    ordering = ['-fecha_busqueda']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'codigo_arancelario', 'tipo_accion', 'resultado_operacion', 'fecha_operacion']
    list_filter = ['tipo_accion', 'resultado_operacion', 'fecha_operacion', 'usuario']
    search_fields = ['codigo_arancelario', 'usuario__username', 'descripcion_clasificacion']
    readonly_fields = ['fecha_operacion']
    ordering = ['-fecha_operacion']
    date_hierarchy = 'fecha_operacion'
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Operación Arancelaria', {
            'fields': ('codigo_arancelario', 'descripcion_clasificacion', 'tipo_accion')
        }),
        ('Resultado', {
            'fields': ('resultado_operacion', 'detalles_adicionales')
        }),
        ('Auditoría', {
            'fields': ('fecha_operacion',)
        }),
    )
