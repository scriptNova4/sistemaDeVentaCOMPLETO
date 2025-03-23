# Despliegue en PythonAnywhere

Este documento contiene los pasos para desplegar el Sistema POS en [PythonAnywhere](https://www.pythonanywhere.com/), un servicio de hosting gratuito para aplicaciones Python.

## 1. Crear una cuenta en PythonAnywhere

Si aún no tienes una cuenta, crea una gratuita en [PythonAnywhere](https://www.pythonanywhere.com/).

## 2. Subir el código a GitHub

Antes de realizar el despliegue, asegúrate de que tu código esté en un repositorio de GitHub. Puedes crear un repositorio y subir tu código con los siguientes comandos:

```bash
git init
git add .
git commit -m "Versión inicial del Sistema POS"
git remote add origin https://github.com/tu-usuario/pos-system.git
git push -u origin master
```

## 3. Configurar PythonAnywhere

Una vez que hayas iniciado sesión en PythonAnywhere, sigue estos pasos:

### 3.1. Crear un entorno virtual

Abre una consola en PythonAnywhere y ejecuta los siguientes comandos:

```bash
mkvirtualenv --python=/usr/bin/python3.8 pos_env
```

### 3.2. Clonar el repositorio

En la misma consola, clona tu repositorio de GitHub:

```bash
git clone https://github.com/tu-usuario/pos-system.git
cd pos-system
```

### 3.3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3.4. Configurar variables de entorno

Crea un archivo `.env` con las siguientes variables:

```bash
echo "FLASK_APP=run.py" >> .env
echo "FLASK_ENV=production" >> .env
echo "SECRET_KEY=tu_clave_secreta_super_segura" >> .env
echo "DATABASE_URL=sqlite:///pos_prod.db" >> .env
```

## 4. Configurar la aplicación web en PythonAnywhere

1. Ve a la sección "Web" en el dashboard de PythonAnywhere.
2. Haz clic en "Add a new web app".
3. Selecciona "Manual configuration".
4. Selecciona "Python 3.8".
5. Configura la ruta al código: `/home/tu-usuario/pos-system`
6. Configura el entorno virtual: `/home/tu-usuario/.virtualenvs/pos_env`

### 4.1. Configurar el archivo WSGI

1. Haz clic en el enlace al archivo WSGI.
2. Reemplaza todo el contenido con lo siguiente:

```python
import sys
import os
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
path = '/home/tu-usuario/pos-system'
if path not in sys.path:
    sys.path.append(path)

# Cargar variables de entorno
load_dotenv(os.path.join(path, '.env'))

# Importar la aplicación
from run import app as application
```

### 4.2. Configurar archivos estáticos

1. En la sección "Static files", agrega la siguiente configuración:
   - URL: `/static/`
   - Path: `/home/tu-usuario/pos-system/app/static/`

## 5. Inicializar la base de datos

Abre una consola en PythonAnywhere y ejecuta:

```bash
cd ~/pos-system
flask db upgrade
python seed.py
```

## 6. Reiniciar la aplicación

1. Vuelve a la sección "Web" en PythonAnywhere.
2. Haz clic en el botón "Reload".

## 7. Acceder a tu aplicación

Tu aplicación ahora estará disponible en `https://tu-usuario.pythonanywhere.com`.

## Notas adicionales

- La cuenta gratuita de PythonAnywhere tiene algunas limitaciones, como la cantidad de tráfico y el uso de CPU.
- La aplicación estará disponible en internet, así que asegúrate de proteger adecuadamente los datos sensibles.
- Para actualizar tu aplicación, simplemente puedes hacer `git pull` en el repositorio y reiniciar la aplicación en PythonAnywhere.
- Para evitar problemas con los archivos estáticos, puedes configurar la opción "Force HTTPS" en la configuración de la aplicación web.
