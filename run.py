import os
from app import create_app, db
from flask_migrate import upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Migrar base de datos a la última revisión
    upgrade()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
