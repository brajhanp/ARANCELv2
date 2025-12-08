# Solución al Error CSRF con ngrok

Si estás obteniendo el error **"CSRF verification failed"** al intentar iniciar sesión a través de ngrok, aquí están las soluciones:

## ✅ Solución Automática (Recomendada)

He creado un middleware personalizado que **automáticamente** permite orígenes de ngrok. Esto debería funcionar sin configuración adicional.

**Solo necesitas reiniciar el servidor Django** después de los cambios:

```powershell
# Detén el servidor (Ctrl+C) y reinícialo
.\run_red.bat
# O si usas ngrok:
.\iniciar_con_ngrok.bat
```

## 🔧 Solución Manual (Si la automática no funciona)

Si el middleware automático no funciona, puedes agregar manualmente tu URL de ngrok:

### Opción 1: Usar el script automático

1. Inicia ngrok primero
2. Ejecuta el script:
   ```powershell
   python agregar_ngrok_url.py
   ```
3. Reinicia el servidor Django

### Opción 2: Agregar manualmente en settings.py

1. Abre `SCMAA/settings.py`
2. Busca la sección `CSRF_TRUSTED_ORIGINS`
3. Agrega tu URL de ngrok:
   ```python
   CSRF_TRUSTED_ORIGINS = [
       'http://localhost:8000',
       'http://127.0.0.1:8000',
       'https://TU-URL-NGROK.ngrok-free.dev',  # Agrega tu URL aquí
   ]
   ```
4. Reinicia el servidor Django

## 📝 Ejemplo

Si tu URL de ngrok es: `https://prelexical-carmelo-tormentedly.ngrok-free.dev`

Agrega esta línea a `CSRF_TRUSTED_ORIGINS`:
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://prelexical-carmelo-tormentedly.ngrok-free.dev',
]
```

## ⚠️ Nota Importante

- **Cada vez que reinicies ngrok**, obtendrás una nueva URL
- Si usas el plan gratuito de ngrok, la URL cambia en cada reinicio
- Para una URL fija, necesitas una cuenta de ngrok (gratuita) y configurar un dominio personalizado

## 🔍 Verificar que funciona

1. Inicia el servidor Django
2. Inicia ngrok
3. Accede a la URL de ngrok
4. Intenta iniciar sesión
5. Si aún ves el error, agrega la URL manualmente como se explica arriba

## 🆘 Si nada funciona

1. Verifica que `DEBUG = True` en `settings.py`
2. Verifica que el middleware personalizado esté activo
3. Revisa los logs del servidor Django para ver errores adicionales
4. Asegúrate de que estás usando la URL HTTPS de ngrok (no HTTP)

