from django import template
from django.urls import reverse
import re

register = template.Library()

# Devuelve una cadena vacía para la tabla si el valor es None o vacío.

@register.filter
def blank_if_none(value):
    return value if value else ""

@register.filter
def get_detail_url(tipo_resultado, id_resultado):
    """Obtiene la URL de detalle basada en el tipo de resultado"""
    if tipo_resultado == 'Sección':
        return f'/arancel/secciones/{id_resultado}/'
    elif tipo_resultado == 'Capítulo':
        return f'/arancel/capitulos/{id_resultado}/'
    elif tipo_resultado == 'Partida':
        return f'/arancel/partidas/{id_resultado}/'
    elif tipo_resultado == 'Subpartida':
        return f'/arancel/subpartidas/{id_resultado}/'
    return '#'

@register.filter
def replace_none(value):
    """Reemplaza None por espacios en blanco"""
    if value is None:
        return ''
    return value

@register.filter
def underscore_to_space(value):
    """Reemplaza guiones bajos por espacios"""
    if value is None:
        return ''
    return str(value).replace('_', ' ')

@register.filter
def is_descriptive_code(value):
    """Devuelve True si el código NO es solo números y puntos (es decir, es un título)."""
    if not value:
        return False
    code_str = str(value).strip()
    # Solo es subpartida normal si contiene solo números y puntos
    if re.fullmatch(r'[0-9.]+', code_str):
        return False  # No es descriptivo, es código válido
    return True  # Es descriptivo (título)