#!/usr/bin/env python
"""
Script para completar `entidad_permiso` y `detalle_permiso` en subpartidas
que ya tienen `requiere_permiso=True` pero carecen de la entidad o del enlace.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SCMAA.settings')
django.setup()

from arancel.models import Subpartida

# Mapeo simple por prefijo de 2 dígitos a entidad y URL
MAP = {
    '01': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '02': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '03': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '04': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '07': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '12': ('SENASAG', 'https://cepbweb.senasag.gob.bo/egp/'),
    '30': ('AGEMED', 'https://rep.agemed.gob.bo/medicamentos-liname/index'),
    '33': ('AGEMED', 'https://rep.agemed.gob.bo/medicamentos-liname/index'),
}

def fix_missing():
    updated = 0
    qs = Subpartida.objects.filter(requiere_permiso=True)
    for s in qs:
        codigo = (s.codigo or '').strip()
        pref = codigo.replace('.', '')[:2] if codigo else ''
        # try to extract first two numeric chars ignoring dots
        if len(pref) < 2:
            # fallback: take first two chars as-is
            pref = (s.codigo or '')[:2]

        info = MAP.get(pref)
        if not info:
            # no mapping known; skip
            continue

        entidad, url = info
        changed = False
        if not s.entidad_permiso or s.entidad_permiso.strip() == '':
            s.entidad_permiso = entidad
            changed = True

        # If detalle_permiso doesn't contain http, replace with URL
        if not s.detalle_permiso or 'http' not in s.detalle_permiso:
            s.detalle_permiso = url
            changed = True

        if changed:
            s.save()
            updated += 1
            print(f"Updated {s.codigo}: entidad={s.entidad_permiso}, url={s.detalle_permiso}")

    print(f"Total updated: {updated}")

if __name__ == '__main__':
    fix_missing()
