# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Aplicación factory pattern"""
    from config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF globalmente en desarrollo

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    login_manager.init_app(app)
    # No inicializar csrf.init_app(app) para deshabilitar CSRF completamente

    # Configurar login manager
    login_manager.login_view = 'auth_controller.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Callback para cargar un usuario desde su ID
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Definir filtro personalizado number_format
    @app.template_filter('number_format')
    def number_format(value, decimals=2):
        """Formatea un número con el número especificado de decimales."""
        return f"{value:,.{decimals}f}".replace(',', ' ')

    # Definir filtro personalizado date
    @app.template_filter('date')
    def date_filter(value, format='%d/%m/%Y %H:%M'):
        """Formatea una fecha con el formato especificado."""
        if value is None:
            return ""
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        return value.strftime(format)

    # Registrar blueprints API (rutas JSON)
    from app.api.products import products_bp
    from app.api.sales import sales_bp
    from app.api.inventory import inventory_bp
    from app.api.customers import customers_bp
    from app.api.suppliers import suppliers_bp
    from app.api.employees import employees_bp
    from app.api.reports import reports_bp
    from app.api.ai_assistant import ai_bp
    from app.auth.routes import auth_bp as auth_api_bp

    app.register_blueprint(auth_api_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    app.register_blueprint(sales_bp, url_prefix='/api/v1/sales')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(customers_bp, url_prefix='/api/v1/customers')
    app.register_blueprint(suppliers_bp, url_prefix='/api/v1/suppliers')
    app.register_blueprint(employees_bp, url_prefix='/api/v1/employees')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')

    # Registrar blueprints de vistas (rutas HTML)
    from app.controllers.main import main
    from app.controllers.auth import auth
    from app.controllers.sales import sales_controller
    from app.controllers.products import products_controller
    from app.controllers.customers import customers_controller
    from app.controllers.inventory import inventory_controller
    from app.controllers.suppliers import suppliers_controller
    from app.controllers.reports import reports_controller
    from app.controllers.ai import ai_controller

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(sales_controller, url_prefix='/sales')
    app.register_blueprint(products_controller, url_prefix='/products')
    app.register_blueprint(customers_controller, url_prefix='/customers')
    app.register_blueprint(inventory_controller, url_prefix='/inventory')
    app.register_blueprint(suppliers_controller, url_prefix='/suppliers')
    app.register_blueprint(reports_controller, url_prefix='/reports')
    app.register_blueprint(ai_controller, url_prefix='/ai')

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db)

    return app