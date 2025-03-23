# Despliegue en Render.com

Este documento contiene los pasos para desplegar el Sistema POS en [Render](https://render.com/), un servicio de hosting con opciones gratuitas para aplicaciones web.

## 1. Crear una cuenta en Render

Si aún no tienes una cuenta, regístrate gratis en [Render](https://render.com/).

## 2. Preparar el código para Render

Antes de desplegar en Render, asegúrate de que tu código esté en un repositorio de GitHub.

### 2.1 Configurar el archivo `render.yaml`

Crea un archivo `render.yaml` en la raíz de tu proyecto con el siguiente contenido:

```yaml
services:
  - type: web
    name: pos-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: FLASK_APP
        value: run.py
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        fromGroup: pos-secrets
      - key: DATABASE_URL
        fromGroup: pos-secrets
```

## 3. Desplegar en Render

### 3.1 Utilizando el Dashboard

1. Inicia sesión en Render.
2. Haz clic en "New" y selecciona "Web Service".
3. Conecta tu repositorio de GitHub (permite a Render acceder a tu repositorio).
4. Selecciona el repositorio del Sistema POS.
5. Configura el servicio:
   - Nombre: `pos-system`
   - Región: Elige la más cercana a tus usuarios
   - Branch: `main` (o `master`)
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
6. En la sección "Environment Variables", añade las siguientes variables:
   - `FLASK_APP`: `run.py`
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Una clave secreta segura
   - `DATABASE_URL`: `sqlite:///pos_prod.db` (para producción, considera usar PostgreSQL)
7. Haz clic en "Create Web Service".

### 3.2 Utilizando el archivo `render.yaml` (Blueprint)

1. Inicia sesión en Render.
2. Haz clic en "New" y selecciona "Blueprint".
3. Conecta tu repositorio de GitHub.
4. Selecciona el repositorio del Sistema POS.
5. Render detectará automáticamente el archivo `render.yaml` y configurará el servicio.
6. Crea un grupo de secretos llamado `pos-secrets` con las siguientes variables:
   - `SECRET_KEY`: Una clave secreta segura
   - `DATABASE_URL`: `sqlite:///pos_prod.db` (para producción, considera usar PostgreSQL)
7. Haz clic en "Apply".

## 4. Configurar la base de datos persistente

Para la versión gratuita de Render, usa SQLite con almacenamiento persistente:

1. En el dashboard de tu servicio, ve a la sección "Disks".
2. Haz clic en "Add Disk".
3. Configura un disco con los siguientes detalles:
   - Nombre: `pos-data`
   - Mount Path: `/opt/render/project/src/data`
   - Tamaño: 1 GB (el mínimo)
4. Actualiza la variable de entorno `DATABASE_URL` a `sqlite:////opt/render/project/src/data/pos_prod.db`

## 5. Inicializar la base de datos

Una vez que el servicio esté desplegado, debes inicializar la base de datos:

1. En el dashboard del servicio, ve a la sección "Shell".
2. Ejecuta los siguientes comandos:
   ```bash
   cd /opt/render/project/src
   flask db upgrade
   python seed.py
   ```

## 6. Acceder a tu aplicación

Tu aplicación estará disponible en la URL proporcionada por Render, algo como `https://pos-system.onrender.com`.

## Notas adicionales

- La cuenta gratuita de Render tiene limitaciones, como el tiempo de actividad del servicio (el servicio se apaga después de 15 minutos de inactividad).
- Para evitar que el servicio se detenga, puedes configurar un servicio de "ping" que haga solicitudes periódicas a tu aplicación.
- Render ofrece integraciones nativas con bases de datos PostgreSQL, lo que es recomendable para entornos de producción.
- Para actualizar tu aplicación, simplemente haz push a tu repositorio en GitHub y Render automáticamente desplegará los cambios.
- Render proporciona HTTPS por defecto para todos los servicios web.
