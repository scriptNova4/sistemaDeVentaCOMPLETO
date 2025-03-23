# app/models/user.py
from datetime import datetime
from app import db, bcrypt
from flask_login import UserMixin  # Importar UserMixin

class User(UserMixin, db.Model):
    """Modelo para usuarios y empleados del sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee, etc.
    is_active = db.Column(db.Boolean, default=True)
    position = db.Column(db.String(50))
    department = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sales = db.relationship('Sale', backref='cashier', lazy='dynamic')

    def __init__(self, username, email, password, fullname, role='employee', **kwargs):
        self.username = username
        self.email = email
        self.password = password
        self.fullname = fullname
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'