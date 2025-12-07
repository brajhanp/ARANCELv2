"""
Script para agregar automáticamente la URL de ngrok a CSRF_TRUSTED_ORIGINS.
Ejecuta este script después de iniciar ngrok para agregar la URL automáticamente.
"""
import os
import sys
import re
from pathlib import Path

# Ruta al archivo settings.py
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / 'SCMAA' / 'settings.py'

def get_ngrok_url():
    """Intenta obtener la URL de ngrok desde la API local."""
    try:
        import requests
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                public_url = tunnels[0].get('public_url')
                if public_url:
                    return public_url
    except Exception:
        pass
    return None

def add_ngrok_to_settings(url):
    """Agrega la URL de ngrok a CSRF_TRUSTED_ORIGINS en settings.py"""
    if not SETTINGS_FILE.exists():
        print(f"Error: No se encontró {SETTINGS_FILE}")
        return False
    
    # Leer el archivo
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si la URL ya está en CSRF_TRUSTED_ORIGINS
    if url in content:
        print(f"La URL {url} ya está en CSRF_TRUSTED_ORIGINS")
        return True
    
    # Buscar la sección CSRF_TRUSTED_ORIGINS
    pattern = r"CSRF_TRUSTED_ORIGINS\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Agregar la nueva URL a la lista
        existing = match.group(1)
        # Limpiar espacios y líneas
        existing = existing.strip()
        if existing and not existing.endswith(','):
            existing += ','
        new_content = existing + f"\n    '{url}',"
        
        # Reemplazar en el contenido
        new_section = f"CSRF_TRUSTED_ORIGINS = [{new_content}\n]"
        content = content[:match.start()] + new_section + content[match.end():]
        
        # Escribir el archivo
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ URL {url} agregada a CSRF_TRUSTED_ORIGINS")
        print("  Reinicia el servidor Django para que los cambios surtan efecto.")
        return True
    else:
        print("Error: No se encontró CSRF_TRUSTED_ORIGINS en settings.py")
        return False

def main():
    print("=" * 50)
    print("  Agregar URL de ngrok a CSRF_TRUSTED_ORIGINS")
    print("=" * 50)
    print()
    
    # Intentar obtener la URL automáticamente
    url = get_ngrok_url()
    
    if url:
        print(f"URL de ngrok detectada: {url}")
        print()
        if add_ngrok_to_settings(url):
            print("\n✓ Configuración actualizada correctamente")
        else:
            print("\n✗ Error al actualizar la configuración")
    else:
        print("No se pudo detectar automáticamente la URL de ngrok.")
        print("Asegúrate de que ngrok esté corriendo en http://127.0.0.1:4040")
        print()
        url = input("Ingresa manualmente la URL de ngrok (ej: https://abc123.ngrok.io): ").strip()
        
        if url:
            if add_ngrok_to_settings(url):
                print("\n✓ Configuración actualizada correctamente")
            else:
                print("\n✗ Error al actualizar la configuración")
        else:
            print("\n✗ No se ingresó ninguna URL")

if __name__ == '__main__':
    main()

