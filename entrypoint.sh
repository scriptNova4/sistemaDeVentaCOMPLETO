#!/bin/bash

# Esperar a que la base de datos esté disponible (solo en caso de usar una BD externa)
# echo "Esperando a que la base de datos esté disponible..."
# python -c 'import time, os, sqlalchemy; db_uri = os.environ.get("DATABASE_URL"); engine = sqlalchemy.create_engine(db_uri); timeout = 60; start_time = time.time(); while True: try: engine.connect(); break; except sqlalchemy.exc.OperationalError: if time.time() - start_time > timeout: raise; time.sleep(1)'

# Ejecutar migraciones
echo "Ejecutando migraciones..."
flask db upgrade || flask db init && flask db migrate && flask db upgrade

# Cargar datos iniciales
echo "Cargando datos iniciales..."
python seed.py

# Iniciar la aplicación
echo "Iniciando la aplicación..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
