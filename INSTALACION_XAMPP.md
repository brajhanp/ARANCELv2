# Guía de Instalación en XAMPP - ARANCELv2

Esta guía te ayudará a configurar el proyecto Django ARANCELv2 para funcionar con XAMPP.

## Opción 1: Método Recomendado (Servidor de Desarrollo Django)

Esta es la forma más simple y recomendada para desarrollo local. Django incluye su propio servidor web que funciona perfectamente con XAMPP.

### Pasos:

1. **Asegúrate de tener XAMPP instalado**
   - Descarga desde: https://www.apachefriends.org/
   - Instala en la ubicación predeterminada (C:\xampp)

2. **Inicia MySQL en XAMPP** (opcional, si quieres usar MySQL en lugar de SQLite)
   - Abre el Panel de Control de XAMPP
   - Haz clic en "Start" junto a MySQL

3. **Prepara el proyecto Django**
   ```powershell
   cd "E:\Downloads\proyecto arancel\ARANCELv2"
   
   # Activa el entorno virtual
   .\venv\Scripts\activate.bat
   
   # Si no tienes el venv, créalo:
   python -m venv venv
   .\venv\Scripts\activate.bat
   pip install -r requirements.txt
   
   # Ejecuta las migraciones
   python manage.py migrate
   
   # Recolecta archivos estáticos
   python manage.py collectstatic --noinput
   ```

4. **Inicia el servidor Django**
   ```powershell
   python manage.py runserver
   ```

5. **Accede a la aplicación**
   - Abre tu navegador en: http://127.0.0.1:8000/
   - O usa: http://localhost:8000/

### Ventajas de este método:
- ✅ No requiere configuración adicional de Apache
- ✅ Funciona inmediatamente
- ✅ Ideal para desarrollo
- ✅ No necesitas mod_wsgi

---

## Opción 2: Integración Completa con Apache (mod_wsgi)

Si necesitas que Django funcione directamente a través de Apache (puerto 80), sigue estos pasos:

### Requisitos Previos:

1. **XAMPP instalado** (C:\xampp)
2. **Python instalado** (versión 3.10 o superior)
3. **mod_wsgi para Windows**

### Instalación de mod_wsgi:

1. **Instala mod_wsgi usando pip:**
   ```powershell
   cd "E:\Downloads\proyecto arancel\ARANCELv2"
   .\venv\Scripts\activate.bat
   pip install mod_wsgi
   ```

2. **Obtén la configuración de mod_wsgi:**
   ```powershell
   mod_wsgi-express module-config
   ```
   
   Esto mostrará algo como:
   ```
   LoadFile "C:/Python312/python312.dll"
   LoadModule wsgi_module "C:/Users/TuUsuario/AppData/Local/Programs/Python/Python312/lib/site-packages/mod_wsgi/server/mod_wsgi.cp312-win_amd64.pyd"
   ```

3. **Configura Apache en XAMPP:**
   
   a. Abre el archivo: `C:\xampp\apache\conf\httpd.conf`
   
   b. Busca la línea que dice `#LoadModule rewrite_module modules/mod_rewrite.so` y descoméntala:
   ```apache
   LoadModule rewrite_module modules/mod_rewrite.so
   ```
   
   c. Agrega las líneas de mod_wsgi que obtuviste en el paso 2 (al final del archivo o después de otros LoadModule)
   
   d. Busca y descomenta la línea:
   ```apache
   Include conf/extra/httpd-vhosts.conf
   ```

4. **Configura el Virtual Host:**
   
   a. Abre: `C:\xampp\apache\conf\extra\httpd-vhosts.conf`
   
   b. Agrega al final el contenido del archivo `xampp_httpd.conf` (ajustando las rutas):
   ```apache
   <VirtualHost *:80>
       ServerName localhost
       
       # AJUSTA ESTA RUTA SEGÚN TU INSTALACIÓN
       WSGIPythonHome "E:/Downloads/proyecto arancel/ARANCELv2/venv"
       WSGIPythonPath "E:/Downloads/proyecto arancel/ARANCELv2"
       
       WSGIScriptAlias / "E:/Downloads/proyecto arancel/ARANCELv2/SCMAA/wsgi.py"
       
       <Directory "E:/Downloads/proyecto arancel/ARANCELv2/SCMAA">
           <Files wsgi.py>
               Require all granted
           </Files>
       </Directory>
       
       Alias /static "E:/Downloads/proyecto arancel/ARANCELv2/staticfiles"
       <Directory "E:/Downloads/proyecto arancel/ARANCELv2/staticfiles">
           Require all granted
       </Directory>
   </VirtualHost>
   ```

5. **Prepara el proyecto:**
   ```powershell
   cd "E:\Downloads\proyecto arancel\ARANCELv2"
   .\venv\Scripts\activate.bat
   python manage.py collectstatic --noinput
   ```

6. **Reinicia Apache desde el Panel de Control de XAMPP**

7. **Accede a la aplicación:**
   - Abre: http://localhost/

---

## Opción 3: Usar el Script Automático

He creado un script que facilita la configuración:

1. **Ejecuta el script de configuración:**
   ```powershell
   cd "E:\Downloads\proyecto arancel\ARANCELv2"
   .\configurar_xampp.bat
   ```

2. **Sigue las instrucciones en pantalla**

---

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'mod_wsgi'"
- **Solución**: Instala mod_wsgi: `pip install mod_wsgi`

### Error: "Forbidden - You don't have permission to access"
- **Solución**: Verifica los permisos en el archivo httpd-vhosts.conf y asegúrate de que las rutas sean correctas

### Error: "AH00558: httpd.exe: Could not reliably determine the server's fully qualified domain name"
- **Solución**: Agrega `ServerName localhost` en httpd.conf

### Los archivos estáticos no se cargan
- **Solución**: Ejecuta `python manage.py collectstatic` y verifica que la ruta en Apache sea correcta

### El servidor Django no inicia
- **Solución**: Verifica que el puerto 8000 no esté en uso: `netstat -ano | findstr :8000`

---

## Recomendación

Para desarrollo local, **usa la Opción 1** (servidor de desarrollo de Django). Es más simple, no requiere configuración adicional y funciona perfectamente.

Para producción o si necesitas que funcione en el puerto 80 de Apache, usa la **Opción 2**.

---

## Contacto y Soporte

Si tienes problemas, verifica:
1. Que Python esté instalado y en el PATH
2. Que el entorno virtual esté activado
3. Que todas las dependencias estén instaladas (`pip install -r requirements.txt`)
4. Que las rutas en los archivos de configuración sean correctas

