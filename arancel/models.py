from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

# Función para convertir números a romanos
def int_to_roman(number):
    if not number:
        return ''
    roman_numerals = {
        1000: 'M', 900: 'CM', 500: 'D', 400: 'CD',
        100: 'C', 90: 'XC', 50: 'L', 40: 'XL',
        10: 'X', 9: 'IX', 5: 'V', 4: 'IV', 1: 'I'
    }
    result = ''
    for value, numeral in sorted(roman_numerals.items(), key=lambda x: x[0], reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result


class Seccion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        # Devuelve un nombre legible incluso si la instancia no tiene id
        if self.id:
            return f"Sección {int_to_roman(self.id)}"
        return self.nombre or 'Sección sin identificar'


class Capitulo(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='capitulos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)  # Agrega este campo

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name='partidas')
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.codigo


class Subpartida(models.Model):
    id = models.AutoField(primary_key=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='subpartidas')
    codigo = models.CharField(max_length=13, unique=True, db_index=True)
    descripcion = models.TextField()
    ga = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # GA %
    ice_iehd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # ICE/IEHD
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    despacho_en_frontera = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos para "Documento Adicional para el despacho aduanero"
    tipo_de_doc = models.CharField(max_length=255, blank=True, null=True)  # Tipo de Doc
    entidad_que_emite = models.CharField(max_length=255, blank=True, null=True)  # Entidad que emite
    disposicion_legal = models.CharField(max_length=255, blank=True, null=True)  # Disp. Legal
    
    # Campos para requisitos adicionales de pre-validación
    requiere_permiso = models.BooleanField(default=False)
    detalle_permiso = models.TextField(blank=True, null=True)
    entidad_permiso = models.CharField(max_length=255, blank=True, null=True)
    estado_permiso = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('no_aplica', 'No aplica')
    ], default='no_aplica')
    
    requiere_licencia = models.BooleanField(default=False)
    detalle_licencia = models.TextField(blank=True, null=True)
    entidad_licencia = models.CharField(max_length=255, blank=True, null=True)
    estado_licencia = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('no_aplica', 'No aplica')
    ], default='no_aplica')
    
    requiere_cupo = models.BooleanField(default=False)
    detalle_cupo = models.TextField(blank=True, null=True)
    entidad_cupo = models.CharField(max_length=255, blank=True, null=True)
    estado_cupo = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('no_aplica', 'No aplica')
    ], default='no_aplica')
    
    instrucciones_validacion = models.TextField(blank=True, null=True)  # Instrucciones específicas para completar requisitos

    # Campos para "Preferencia Arancelaria"
    can_ace_36_47_ven = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # CAN ACE 36 ACE 47 VEN
    ace_22_chile = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # ACE 22 Chile
    ace_22_prot = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # ACE 22 Prot
    ace_66_mexico = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # ACE 66 México

    # Campos para vigencia / control de validez
    fecha_vigencia_inicio = models.DateField(blank=True, null=True)
    fecha_vigencia_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.codigo

    @property
    def vigente(self):
        """Indica si la subpartida se encuentra vigente en la fecha actual.

        Regla: si ambas fechas están presentes se verifica el rango, si falta una fecha
        se interpreta de forma abierta en esa dirección. Si no hay información devuelve False.
        """
        today = timezone.localdate()
        if self.fecha_vigencia_inicio and self.fecha_vigencia_fin:
            return self.fecha_vigencia_inicio <= today <= self.fecha_vigencia_fin
        if self.fecha_vigencia_inicio and not self.fecha_vigencia_fin:
            return self.fecha_vigencia_inicio <= today
        if self.fecha_vigencia_fin and not self.fecha_vigencia_inicio:
            return today <= self.fecha_vigencia_fin
        return False

    def clean(self):
        """Validaciones de modelo para asegurar formato correcto de código arancelario.

        - Código debe ser numérico (solo dígitos) y tener entre 6 y 13 caracteres (ajustable).
        - Validación ligera para evitar insertar códigos claramente inválidos.
        """
        super().clean()
        if self.codigo:
            codigo = str(self.codigo).strip()
            # Validar que el código contenga solo dígitos y puntos
            # Primero removemos los puntos para validar la longitud de los dígitos
            codigo_sin_puntos = codigo.replace('.', '')
            
            # Validar que sean solo dígitos y puntos
            if not re.match(r'^[\d.]+$', codigo):
                raise ValidationError({'codigo': 'El código arancelario debe contener solo dígitos y puntos.'})
                
            # Validar que la cantidad de dígitos esté entre 6 y 13
            if not (6 <= len(codigo_sin_puntos) <= 13):
                raise ValidationError({'codigo': 'El código arancelario debe tener entre 6 y 13 dígitos (sin contar puntos).'})
