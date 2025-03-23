# Sistema de Punto de Venta (POS)

Un sistema completo de punto de venta con gestión de inventario, ventas, clientes, proveedores y recomendaciones inteligentes mediante IA.

## Características

- **Punto de Venta (POS)**: Interfaz rápida y amigable para el cajero, escaneo de productos, múltiples métodos de pago y generación de tickets.
- **Gestión de Inventario**: Control de stock en tiempo real, alertas de productos por agotarse, y gestión de entradas y salidas.
- **Gestión de Clientes**: Historial de compras, programas de fidelización, créditos y cuentas por cobrar.
- **Gestión de Proveedores**: Registro de proveedores, historial de compras y pedidos automatizados.
- **Gestión de Empleados**: Registro de usuarios con diferentes roles y permisos.
- **Reportes**: Estadísticas y reportes financieros en tiempo real.
- **Asistente de IA**: Análisis de datos y recomendaciones inteligentes para mejorar ventas e inventario.

## Tecnologías

- **Backend**: Python con Flask, SQLAlchemy
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Inteligencia Artificial**: Scikit-learn para análisis de datos y recomendaciones
- **Despliegue**: Docker, Gunicorn

## Requerimientos

- Python 3.8+
- Docker (opcional para despliegue en producción)

## Instalación

### Desarrollo local

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/pos-system.git
   cd pos-system
   ```

2. Crear un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno (crear un archivo `.env` en la raíz del proyecto):
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=tu_clave_secreta
   DATABASE_URL=sqlite:///pos_dev.db
   ```

5. Inicializar la base de datos:
   ```
   flask db upgrade
   python seed.py
   ```

6. Ejecutar la aplicación:
   ```
   flask run
   ```

### Despliegue con Docker

1. Construir y levantar los contenedores:
   ```
   docker-compose up -d --build
   ```

2. La aplicación estará disponible en `http://localhost:5000`

## Acceso a la aplicación

El sistema viene con usuarios predefinidos para empezar a utilizarlo:

- **Administrador**:
  - Usuario: admin
  - Contraseña: admin123

- **Gerente**:
  - Usuario: gerente
  - Contraseña: gerente123

- **Cajero**:
  - Usuario: cajero
  - Contraseña: cajero123

## Estructura del Proyecto

```
pos_system/
├── app/                    # Aplicación principal
│   ├── api/                # API REST
│   ├── auth/               # Autenticación API
│   ├── controllers/        # Controladores de vistas
│   ├── models/             # Modelos de datos
│   ├── services/           # Servicios y lógica de negocio
│   ├── static/             # Archivos estáticos (CSS, JS)
│   ├── templates/          # Plantillas HTML
│   └── utils/              # Utilidades varias
├── migrations/             # Migraciones de la base de datos
├── config.py               # Configuración de la aplicación
├── requirements.txt        # Dependencias
├── run.py                  # Punto de entrada de la aplicación
├── seed.py                 # Script para cargar datos iniciales
├── Dockerfile              # Configuración Docker
└── docker-compose.yml      # Configuración Docker Compose
```

## Adaptación a Diferentes Negocios

El sistema está diseñado para ser adaptable a diferentes tipos de negocios:

1. **Configuración del catálogo**: Personaliza categorías y productos según el tipo de negocio.
2. **Personalización de informes**: Configura los informes según las necesidades específicas del negocio.
3. **Ajustes fiscales**: Configura impuestos y parámetros fiscales según la región.
4. **Interfaz personalizable**: Adapta la interfaz según las necesidades del negocio.

## Contribución

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añade nueva característica'`)
4. Sube tu rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.
