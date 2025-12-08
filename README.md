# ARANCELv2 - Sistema de Gestión Arancelaria

Sistema Django completo para gestión de aranceles aduanales, clasificación de productos y trazabilidad de operaciones.

## Requisitos Previos

- **Python 3.10+** (descarga desde [python.org](https://www.python.org/))
- **Git** (opcional, para clonar el repositorio)
- **Windows** (para usar `setup.bat`)

## Instalación Rápida (Windows)

### Opción 1: Usar el Script de Setup (Recomendado)

1. **Descarga o clona el proyecto**
   ```bash
   git clone https://github.com/brajhanp/ARANCELv2.git
   cd ARANCELv2-main
   ```

2. **Ejecuta el script de setup**
   - Haz doble clic en `setup.bat`
   - O abre PowerShell/CMD y ejecuta: `.\setup.bat`

3. El script automáticamente:
   - Crea un entorno virtual (`venv`)
   - Instala todas las dependencias (`requirements.txt`)
   - Ejecuta las migraciones de la base de datos

### Opción 2: Instalación Manual

1. **Crea un entorno virtual**
   ```powershell
   python -m venv venv
   ```

2. **Activa el entorno virtual**
   ```powershell
   .\venv\Scripts\activate.bat
   ```

3. **Instala las dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Ejecuta las migraciones**
   ```powershell
   python manage.py migrate
   ```

## Ejecución del Proyecto

### Iniciar el Servidor de Desarrollo

1. **Asegúrate de que el venv está activado**
   ```powershell
   .\venv\Scripts\activate.bat
   ```

2. **Inicia el servidor**
   ```powershell
   python manage.py runserver
   ```

3. **Abre en tu navegador**
   - http://127.0.0.1:8000/

### Datos de la Base de Datos

La base de datos (`db.sqlite3`) **está incluida en el repositorio** con datos de demostración.
- Contiene información de capítulos, partidas, subpartidas y reportes de trazabilidad.
- Se restaura automáticamente al clonar/descargar el proyecto.

## Estructura del Proyecto

```
ARANCELv2/
├── manage.py                 # Gestor de Django
├── requirements.txt          # Dependencias Python
├── db.sqlite3               # Base de datos SQLite con datos
├── setup.bat                # Script de configuración automática
├── README.md                # Este archivo
├── SCMAA/                   # Configuración principal Django
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── arancel/                 # Aplicación de gestión arancelaria
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── templates/
│   └── migrations/
├── central/                 # Aplicación central (reportes, usuarios, auth)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── templates/
│   └── migrations/
└── templates/               # Templates globales
    └── base.html
```

## Características Principales

### 1. Gestión de Aranceles
- Búsqueda de capítulos, partidas y subpartidas arancelarias
- Visualización de gravámenes y detalles de clasificación
- Prevalidación de códigos arancelarios

### 2. Sistema de Trazabilidad
- Registro automático de todas las operaciones (búsquedas, descargas, accesos)
- Reportes detallados con filtros por usuario, fecha, código
- Exportación a **PDF y Excel**
- **Control de permisos por rol:**
  - **Gerentes y Superusuarios**: ven todos los reportes y pueden filtrar por usuario en historial
  - **Despachantes de Aduanas (usuarios normales)**: solo ven sus propios reportes e historial
  - Campo "Usuario" disponible solo en **Historial de Búsquedas** para gerentes/superusuarios

### 3. Autenticación y Control de Acceso
- Login de usuarios con roles
- Historial de operaciones por usuario
- Acceso restringido a reportes y funciones administrativas

### 4. Panel Administrativo
- Interfaz de Django Admin para gestionar datos
- Acceso: http://127.0.0.1:8000/admin/

## Comandos Útiles

### Crear un Superusuario (Admin)
```powershell
python manage.py createsuperuser
```

### Ejecutar Migraciones de Base de Datos
```powershell
python manage.py migrate
```

### Crear Migraciones desde Cambios de Modelos
```powershell
python manage.py makemigrations
```

### Acceder al Shell Django
```powershell
python manage.py shell
```

### Recolectar Archivos Estáticos (para producción)
```powershell
python manage.py collectstatic
```

### Comando personalizado: `actualizar_permisos`

Este proyecto incluye un comando de administración para normalizar y actualizar los campos relacionados con permisos en las subpartidas.

- **Qué hace:**
   - Añade el enlace de la Ventanilla Única de Comercio (VUCE) `https://www.vuce.gob.bo` a las subpartidas cuyo `tipo_de_doc` es `C` o `C-CITES` (sin duplicar).
   - Establece valores por defecto de `entidad_permiso` para `C` (SENASAG) y `C-CITES` (MDRYT / MMAYA) cuando estén vacíos.
   - Limpia (`entidad_permiso`, `detalle_permiso`, `requiere_permiso`, `estado_permiso`) en subpartidas de otros tipos, marcándolas como `no_aplica`.

- **Cómo ejecutarlo:**
```powershell
py manage.py actualizar_permisos
```

Usa este comando con precaución en entornos de producción; crea una copia de seguridad de `db.sqlite3` antes de ejecutar si corresponde.


## Solución de Problemas

### Error: "python: command not found"
- **Solución**: Instala Python desde [python.org](https://www.python.org/) y asegúrate de marcar "Add Python to PATH" durante la instalación.

### Error: "No module named 'django'"
- **Solución**: Verifica que el venv está activado y ejecuta:
  ```powershell
  pip install -r requirements.txt
  ```

### Error: "ModuleNotFoundError: No module named 'venv'"
- **Solución**: Tu versión de Python no incluye venv. Instala una versión más reciente (3.10+).

### Base de datos no aparece
### Error: "No module named 'spellchecker'" o problemas con pyspellchecker

- **Síntoma:** Iniciar el servidor con `python manage.py runserver` lanza `ModuleNotFoundError: No module named 'spellchecker'` o errores relacionados.
- **Causa:** El proyecto usa `pyspellchecker` en `arancel/views.py` para mejora de sugerencias ortográficas; si la dependencia no está instalada en el entorno virtual, Django fallará al importar.
- **Solución:**
  1. Activa tu entorno virtual (si procede):
     ```powershell
     .\venv\Scripts\activate.bat
     ```
  2. Instala las dependencias:
     ```powershell
     pip install -r requirements.txt
     ```
  3. Alternativa rápida (solo `pyspellchecker`):
     ```powershell
     pip install pyspellchecker
     ```

- **Opción si no quieres usar la corrección ortográfica:** comenta o elimina la importación en `arancel/views.py` (`from spellchecker import SpellChecker`) y las secciones que la utilicen. Esto es seguro y solo desactiva la sugerencia ortográfica.

- **Solución**: Ejecuta:
  ```powershell
  python manage.py migrate
  ```

## Dependencias

El proyecto usa las siguientes librerías Python:

- **Django 5.2.1** - Framework web
- **asgiref 3.8.1** - ASGI server interface
- **sqlparse 0.5.3** - Parser de SQL
- **tzdata 2025.2** - Datos de zonas horarias

Ver `requirements.txt` para la lista completa.

## Despliegue a Producción

Para desplegar en producción:

1. Cambiar `DEBUG = False` en `SCMAA/settings.py`
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Usar un servidor WSGI (Gunicorn, uWSGI)
4. Configurar SSL/HTTPS
5. Usar una base de datos robusta (PostgreSQL recomendado)

Consulta la [documentación oficial de Django](https://docs.djangoproject.com/en/5.2/howto/deployment/) para más detalles.

## Soporte y Contacto

- **Repositorio**: https://github.com/brajhanp/ARANCELv2
- **Autor**: Brajhan P.

## Licencia

Este proyecto es de uso educativo y demostrativo.

---

**Última actualización**: 7 de Diciembre de 2025

### Cambios Recientes (v2.1.0)
- ✅ Movimiento del buscador de usuario: ahora solo disponible en **Historial de Búsquedas** (antes estaba en Reportes)
- ✅ Restricciones de permisos en Reportes: solo gerentes/superusuarios ven todos; usuarios normales ven solo sus propios reportes
- ✅ Campo "Usuario" visible solo para roles autorizados (Gerente y Superusuario) en Historial
- ✅ Corrección de sintaxis en plantilla de Historial de Búsquedas
