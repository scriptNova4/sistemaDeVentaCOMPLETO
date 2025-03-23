# app/controllers/inventory.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, InventoryMovement

inventory_controller = Blueprint('inventory_controller', __name__)

@inventory_controller.route('/stock')
@login_required
def stock():
    """Ver existencias de productos"""
    products = Product.query.all()
    return render_template('inventory/stock.html', products=products)

@inventory_controller.route('/movements')
@login_required
def movements():
    """Ver movimientos de inventario"""
    movements = InventoryMovement.query.order_by(InventoryMovement.created_at.desc()).all()
    return render_template('inventory/movements.html', movements=movements)

@inventory_controller.route('/adjustments', methods=['GET', 'POST'])
@login_required
def adjustments():
    """Ajustar inventario"""
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            quantity = int(request.form['quantity'])
            movement_type = request.form['movement_type']
            reference = request.form.get('reference')
            notes = request.form.get('notes')

            product = Product.query.get_or_404(product_id)
            if movement_type == 'entrada':
                product.stock += quantity
            elif movement_type == 'salida':
                if product.stock < quantity:
                    flash('Stock insuficiente para realizar la salida', 'danger')
                    return redirect(url_for('inventory_controller.adjustments'))
                product.stock -= quantity

            movement = InventoryMovement(
                product_id=product_id,
                quantity=quantity if movement_type == 'entrada' else -quantity,
                movement_type=movement_type,
                reference=reference,
                notes=notes,
                user_id=current_user.id
            )
            db.session.add(movement)
            db.session.commit()
            flash('Ajuste de inventario realizado con éxito', 'success')
            return redirect(url_for('inventory_controller.stock'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al realizar el ajuste: {str(e)}', 'danger')

    products = Product.query.all()
    return render_template('inventory/adjustments.html', products=products)