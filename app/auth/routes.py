# app/auth/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from datetime import datetime
from flask_wtf.csrf import CSRFProtect  # Importar CSRFProtect en lugar de csrf

auth_bp = Blueprint('auth', __name__)
csrf = CSRFProtect()  # Crear una instancia de CSRFProtect

@auth_bp.route('/register', methods=['POST'])
@csrf.exempt  # Deshabilitar CSRF para esta ruta
def register():
    """Registrar un nuevo usuario"""
    data = request.json

    # Verificar si el usuario ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El correo electrónico ya está en uso'}), 400

    # Crear nuevo usuario
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            fullname=data['fullname'],
            role=data.get('role', 'employee')
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'Usuario registrado con éxito',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'fullname': user.fullname,
                'role': user.role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión con usuario y contraseña"""
    data = request.json

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.verify_password(data['password']):
        return jsonify({'error': 'Nombre de usuario o contraseña incorrectos'}), 401

    if not user.is_active:
        return jsonify({'error': 'Cuenta desactivada. Contacte al administrador'}), 401

    # Actualizar último inicio de sesión
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Crear token de acceso
    access_token = create_access_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'fullname': user.fullname,
            'role': user.role
        }
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario autenticado"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'fullname': user.fullname,
        'role': user.role,
        'position': user.position,
        'department': user.department,
        'phone': user.phone,
        'last_login': user.last_login
    })

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario autenticado"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.json

    # Actualizar datos del usuario
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'El correo electrónico ya está en uso'}), 400
        user.email = data['email']

    if 'fullname' in data:
        user.fullname = data['fullname']

    if 'phone' in data:
        user.phone = data['phone']

    if 'password' in data:
        user.password = data['password']

    try:
        db.session.commit()
        return jsonify({'message': 'Perfil actualizado con éxito'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500