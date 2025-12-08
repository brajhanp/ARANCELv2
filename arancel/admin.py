from django.contrib import admin
from .models import Seccion, Capitulo, Partida, Subpartida

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion', 'seccion')

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')

@admin.register(Subpartida)
class SubpartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'ga', 'ice_iehd', 'unidad_medida', 'is_vigente')
    readonly_fields = ('is_vigente',)

    def is_vigente(self, obj):
        try:
            return obj.vigente
        except Exception:
            return False
    is_vigente.boolean = True
    is_vigente.short_description = 'Vigente'
