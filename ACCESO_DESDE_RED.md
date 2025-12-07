# Guía: Acceso desde Otros Dispositivos en Cualquier Red

Esta guía te mostrará cómo hacer que tu aplicación Django sea accesible desde otros dispositivos, tanto en tu red local como desde internet.

---

## 🏠 Opción 1: Acceso desde Red Local (Misma WiFi)

Esta es la opción más simple y segura para compartir la aplicación en tu casa u oficina.

### Paso 1: Configurar el Servidor

1. **Ejecuta el servidor en modo red:**
   ```powershell
   cd "E:\Downloads\proyecto arancel\ARANCELv2"
   .\run_red.bat
   ```
   
   O manualmente:
   ```powershell
   .\venv\Scripts\activate.bat
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Obtén tu IP local:**
   ```powershell
   .\obtener_ip.bat
   ```
   
   O manualmente:
   ```powershell
   ipconfig
   ```
   Busca "IPv4" y copia la dirección (ejemplo: 192.168.1.100)

### Paso 2: Configurar el Firewall de Windows

1. **Abre el Firewall de Windows:**
   - Presiona `Win + R`
   - Escribe: `wf.msc` y presiona Enter

2. **Crea una regla de entrada:**
   - Click en "Reglas de entrada" → "Nueva regla"
   - Selecciona "Puerto" → Siguiente
   - Selecciona "TCP" y escribe `8000` → Siguiente
   - Selecciona "Permitir la conexión" → Siguiente
   - Marca todas las opciones (Dominio, Privada, Pública) → Siguiente
   - Nombre: "Django ARANCELv2" → Finalizar

   **O usa el script automático:**
   ```powershell
   netsh advfirewall firewall add rule name="Django ARANCELv2" dir=in action=allow protocol=TCP localport=8000
   ```

### Paso 3: Acceder desde Otros Dispositivos

1. **Asegúrate de que todos los dispositivos estén en la misma red WiFi**

2. **Desde otro dispositivo (celular, tablet, otra PC):**
   - Abre el navegador
   - Ve a: `http://TU_IP_LOCAL:8000`
   - Ejemplo: `http://192.168.1.100:8000`

---

## 🌐 Opción 2: Acceso desde Internet (Cualquier Red)

Para acceder desde cualquier lugar del mundo, necesitas exponer tu servidor a internet. Aquí tienes varias opciones:

### A) Usando ngrok (Más Fácil - Recomendado)

**ngrok** crea un túnel seguro a tu servidor local.

1. **Descarga ngrok:**
   - Ve a: https://ngrok.com/download
   - Descarga la versión para Windows
   - Extrae el archivo `ngrok.exe` en una carpeta (ej: `C:\ngrok\`)

2. **Inicia tu servidor Django:**
   ```powershell
   .\run_red.bat
   ```

3. **En otra ventana de PowerShell, ejecuta ngrok:**
   ```powershell
   cd C:\ngrok
   .\ngrok.exe http 8000
   ```

4. **Obtén tu URL pública:**
   - ngrok mostrará algo como: `https://abc123.ngrok.io`
   - Esta URL es accesible desde cualquier dispositivo con internet
   - **Nota:** La URL gratuita cambia cada vez que reinicias ngrok

5. **Para una URL fija (requiere cuenta gratuita):**
   ```powershell
   .\ngrok.exe http 8000 --domain=tu-dominio.ngrok-free.app
   ```

**Ventajas:**
- ✅ Muy fácil de usar
- ✅ HTTPS incluido
- ✅ No requiere configuración de router
- ✅ Funciona detrás de firewalls

**Desventajas:**
- ⚠️ URL gratuita cambia al reiniciar
- ⚠️ Límite de conexiones en plan gratuito

---

### B) Usando Cloudflare Tunnel (Gratis y Permanente)

**Cloudflare Tunnel** es una alternativa gratuita y más robusta.

1. **Instala cloudflared:**
   - Descarga desde: https://github.com/cloudflare/cloudflared/releases
   - Extrae `cloudflared.exe` en una carpeta

2. **Inicia el túnel:**
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```

3. **Obtén tu URL:** Cloudflare te dará una URL permanente tipo `https://random-words.trycloudflare.com`

---

### C) Configurar Router (Acceso Directo)

Para acceso directo sin servicios externos, necesitas configurar tu router.

1. **Obtén tu IP pública:**
   - Ve a: https://www.whatismyip.com/
   - Anota tu IP pública

2. **Configura Port Forwarding en tu router:**
   - Accede a la configuración del router (normalmente `192.168.1.1` o `192.168.0.1`)
   - Busca "Port Forwarding" o "Virtual Server"
   - Crea una regla:
     - Puerto externo: 8000
     - Puerto interno: 8000
     - IP interna: Tu IP local (ej: 192.168.1.100)
     - Protocolo: TCP

3. **Accede desde internet:**
   - URL: `http://TU_IP_PUBLICA:8000`
   - **Nota:** La IP pública puede cambiar si no tienes IP estática

**⚠️ ADVERTENCIA DE SEGURIDAD:**
- No uses este método en producción sin HTTPS
- Exponer directamente a internet puede ser inseguro
- Considera usar un servidor proxy reverso (nginx) con SSL

---

## 🔒 Opción 3: Despliegue en Servidor Cloud (Producción)

Para un acceso profesional y seguro desde cualquier lugar:

### Servicios Recomendados:

1. **Render** (Gratis para empezar)
   - https://render.com
   - Conecta tu repositorio GitHub
   - Despliegue automático

2. **Railway** (Gratis con límites)
   - https://railway.app
   - Muy fácil de usar
   - Despliegue en minutos

3. **Heroku** (Pago)
   - https://www.heroku.com
   - Muy popular para Django

4. **DigitalOcean** (Desde $5/mes)
   - https://www.digitalocean.com
   - Control total del servidor

5. **AWS / Google Cloud / Azure**
   - Para proyectos más grandes
   - Más configuración requerida

---

## 📱 Acceso desde Dispositivos Móviles

Una vez que tengas el servidor corriendo:

### Desde Android/iOS:
1. Abre el navegador
2. Ingresa la URL (local o pública según tu configuración)
3. Ejemplo: `http://192.168.1.100:8000` o `https://tu-url.ngrok.io`

### Crear un Acceso Rápido:
- **Android:** Agrega un bookmark en la pantalla de inicio
- **iOS:** Comparte la página → "Agregar a pantalla de inicio"

---

## 🛠️ Solución de Problemas

### "No puedo acceder desde otro dispositivo en la misma red"
- ✅ Verifica que ambos dispositivos estén en la misma WiFi
- ✅ Verifica que el firewall permita el puerto 8000
- ✅ Asegúrate de usar la IP correcta (no 127.0.0.1)
- ✅ Verifica que el servidor esté corriendo en `0.0.0.0:8000`

### "La conexión se cierra después de un tiempo"
- ✅ Usa un servicio como ngrok o Cloudflare Tunnel
- ✅ O configura un servicio de Windows para mantener el servidor activo

### "Error: DisallowedHost"
- ✅ Verifica que `ALLOWED_HOSTS = ['*']` en `settings.py`
- ✅ O agrega tu IP específica: `ALLOWED_HOSTS = ['192.168.1.100']`

### "El servidor es muy lento desde otros dispositivos"
- ✅ Verifica la velocidad de tu red WiFi
- ✅ Considera usar un servidor de producción (Gunicorn + Nginx)

---

## 📋 Resumen Rápido

### Para Red Local:
```powershell
# 1. Inicia el servidor
.\run_red.bat

# 2. Obtén tu IP
.\obtener_ip.bat

# 3. Configura firewall (una sola vez)
netsh advfirewall firewall add rule name="Django ARANCELv2" dir=in action=allow protocol=TCP localport=8000

# 4. Accede desde otros dispositivos: http://TU_IP:8000
```

### Para Internet (ngrok):
```powershell
# 1. Inicia el servidor
.\run_red.bat

# 2. En otra ventana, ejecuta ngrok
ngrok http 8000

# 3. Usa la URL que ngrok te proporciona
```

---

## 🔐 Recomendaciones de Seguridad

1. **Para desarrollo:** Usa ngrok o Cloudflare Tunnel (más seguro)
2. **Para producción:** Usa un servicio cloud con HTTPS
3. **Nunca expongas directamente** sin HTTPS en producción
4. **Cambia `DEBUG = False`** cuando expongas a internet
5. **Usa un SECRET_KEY diferente** para producción

---

¿Necesitas ayuda con alguna opción específica? ¡Dime cuál prefieres y te ayudo a configurarla!

