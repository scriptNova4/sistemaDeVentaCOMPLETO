# app/controllers/customers.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Customer, LoyaltyProgram, LoyaltyTransaction

customers_controller = Blueprint('customers_controller', __name__)

@customers_controller.route('/customers')
@login_required
def list_customers():
    """Lista de clientes"""
    customers = Customer.query.all()
    return render_template('customers/list_customers.html', customers=customers)

@customers_controller.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    """Crear un nuevo cliente"""
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                credit_limit=float(request.form.get('credit_limit', 0))
            )
            db.session.add(customer)
            db.session.commit()
            flash('Cliente creado con éxito', 'success')
            return redirect(url_for('customers_controller.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el cliente: {str(e)}', 'danger')
    return render_template('customers/new_customer.html')

@customers_controller.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """Editar un cliente existente"""
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.email = request.form['email']
            customer.phone = request.form.get('phone')
            customer.address = request.form.get('address')
            customer.credit_limit = float(request.form.get('credit_limit', 0))
            db.session.commit()
            flash('Cliente actualizado con éxito', 'success')
            return redirect(url_for('customers_controller.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el cliente: {str(e)}', 'danger')
    return render_template('customers/edit_customer.html', customer=customer)

@customers_controller.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Eliminar un cliente"""
    customer = Customer.query.get_or_404(customer_id)
    try:
        customer.status = 'inactive'
        db.session.commit()
        flash('Cliente desactivado con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desactivar el cliente: {str(e)}', 'danger')
    return redirect(url_for('customers_controller.list_customers'))

@customers_controller.route('/loyalty')
@login_required
def loyalty():
    """Programa de fidelización"""
    programs = LoyaltyProgram.query.all()
    return render_template('customers/loyalty.html', programs=programs)

@customers_controller.route('/loyalty/new', methods=['GET', 'POST'])
@login_required
def new_loyalty_program():
    """Crear un nuevo programa de fidelización"""
    if request.method == 'POST':
        try:
            program = LoyaltyProgram(
                name=request.form['name'],
                description=request.form.get('description'),
                points_per_purchase=float(request.form.get('points_per_purchase', 1.0)),
                points_to_currency=float(request.form.get('points_to_currency', 0.01)),
                min_points_to_redeem=int(request.form.get('min_points_to_redeem', 100))
            )
            db.session.add(program)
            db.session.commit()
            flash('Programa de fidelización creado con éxito', 'success')
            return redirect(url_for('customers_controller.loyalty'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el programa: {str(e)}', 'danger')
    return render_template('customers/new_loyalty.html')