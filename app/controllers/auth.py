# app/controllers/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User
from datetime import datetime
import uuid

auth = Blueprint('auth_controller', __name__)  # Cambia 'auth' por 'auth_controller'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario desde la sesión"""
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form

        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            if not user.is_active:
                flash('Cuenta desactivada. Contacte al administrador.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth_controller.login'))  # Actualiza el nombre del blueprint aquí

@auth.route('/profile')
@login_required
def profile():
    """Perfil de usuario"""
    return render_template('auth/profile.html')

@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil de usuario"""
    if request.method == 'POST':
        email = request.form.get('email')
        fullname = request.form.get('fullname')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Verificar si se está actualizando el correo y si ya existe
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('El correo electrónico ya está en uso', 'danger')
                return redirect(url_for('auth_controller.edit_profile'))  # Actualiza el nombre del blueprint aquí

        # Actualizar información básica
        current_user.email = email
        current_user.fullname = fullname

        # Actualizar contraseña si se proporciona
        if current_password and new_password:
            if not current_user.verify_password(current_password):
                flash('La contraseña actual es incorrecta', 'danger')
                return redirect(url_for('auth_controller.edit_profile'))  # Actualiza el nombre del blueprint aquí

            current_user.password = new_password
            flash('Contraseña actualizada correctamente', 'success')

        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth_controller.profile'))  # Actualiza el nombre del blueprint aquí

    return render_template('auth/edit_profile.html')

@auth.route('/settings')
@login_required
def settings():
    """Configuración de la cuenta"""
    return render_template('auth/settings.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Solicitar restablecimiento de contraseña"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generar token único para restablecer contraseña
            token = str(uuid.uuid4())
            session['reset_token'] = token
            session['reset_email'] = email

            # En un sistema real, enviaríamos un correo electrónico con un enlace
            # para restablecer la contraseña. Aquí solo simulamos este proceso.
            flash('Se ha enviado un enlace para restablecer tu contraseña a tu correo electrónico', 'success')

            # Redirigir a la página para ingresar una nueva contraseña
            # En un sistema real, este enlace se enviaría por correo
            return redirect(url_for('auth_controller.new_password', token=token))  # Actualiza el nombre del blueprint aquí
        else:
            flash('No se encontró ninguna cuenta con ese correo electrónico', 'danger')

    return render_template('auth/reset_password.html')

@auth.route('/new-password/<token>', methods=['GET', 'POST'])
def new_password(token):
    """Establecer nueva contraseña"""
    # Verificar que el token es válido
    if token != session.get('reset_token'):
        flash('El enlace para restablecer la contraseña no es válido o ha expirado', 'danger')
        return redirect(url_for('auth_controller.login'))  # Actualiza el nombre del blueprint aquí

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('auth_controller.new_password', token=token))  # Actualiza el nombre del blueprint aquí

        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()

        if user:
            user.password = password
            db.session.commit()

            # Limpiar sesión
            session.pop('reset_token', None)
            session.pop('reset_email', None)

            flash('Tu contraseña ha sido restablecida correctamente', 'success')
            return redirect(url_for('auth_controller.login'))  # Actualiza el nombre del blueprint aquí
        else:
            flash('Usuario no encontrado', 'danger')

    return render_template('auth/new_password.html')