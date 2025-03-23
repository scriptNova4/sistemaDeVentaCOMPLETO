# app/controllers/suppliers.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Supplier, PurchaseOrder, PurchaseOrderItem, Product
from datetime import datetime

suppliers_controller = Blueprint('suppliers_controller', __name__)

@suppliers_controller.route('/suppliers')
@login_required
def list_suppliers():
    """Lista de proveedores"""
    suppliers = Supplier.query.all()
    return render_template('suppliers/list_suppliers.html', suppliers=suppliers)

@suppliers_controller.route('/suppliers/new', methods=['GET', 'POST'])
@login_required
def new_supplier():
    """Crear un nuevo proveedor"""
    if request.method == 'POST':
        try:
            supplier = Supplier(
                name=request.form['name'],
                contact_name=request.form.get('contact_name'),
                email=request.form['email'],
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                payment_terms=request.form.get('payment_terms')
            )
            db.session.add(supplier)
            db.session.commit()
            flash('Proveedor creado con éxito', 'success')
            return redirect(url_for('suppliers_controller.list_suppliers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el proveedor: {str(e)}', 'danger')
    return render_template('suppliers/new_supplier.html')

@suppliers_controller.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    """Editar un proveedor existente"""
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        try:
            supplier.name = request.form['name']
            supplier.contact_name = request.form.get('contact_name')
            supplier.email = request.form['email']
            supplier.phone = request.form.get('phone')
            supplier.address = request.form.get('address')
            supplier.payment_terms = request.form.get('payment_terms')
            db.session.commit()
            flash('Proveedor actualizado con éxito', 'success')
            return redirect(url_for('suppliers_controller.list_suppliers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el proveedor: {str(e)}', 'danger')
    return render_template('suppliers/edit_supplier.html', supplier=supplier)

@suppliers_controller.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    """Eliminar un proveedor"""
    supplier = Supplier.query.get_or_404(supplier_id)
    try:
        supplier.status = 'inactive'
        db.session.commit()
        flash('Proveedor desactivado con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desactivar el proveedor: {str(e)}', 'danger')
    return redirect(url_for('suppliers_controller.list_suppliers'))

@suppliers_controller.route('/purchase_orders')
@login_required
def purchase_orders():
    """Lista de órdenes de compra"""
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('suppliers/purchase_orders.html', orders=orders)

@suppliers_controller.route('/purchase_orders/new', methods=['GET', 'POST'])
@login_required
def new_purchase_order():
    """Crear una nueva orden de compra"""
    if request.method == 'POST':
        try:
            supplier_id = request.form['supplier_id']
            product_ids = request.form.getlist('product_id')
            quantities = request.form.getlist('quantity')

            order = PurchaseOrder(
                order_number=f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                supplier_id=supplier_id,
                user_id=current_user.id,
                total=0,
                status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            total = 0
            for product_id, quantity in zip(product_ids, quantities):
                quantity = int(quantity)
                if quantity <= 0:
                    continue
                product = Product.query.get(product_id)
                if not product:
                    continue
                item = PurchaseOrderItem(
                    purchase_order=order,
                    product_id=product_id,
                    quantity=quantity,
                    cost=product.cost,
                    total=product.cost * quantity
                )
                total += product.cost * quantity
                db.session.add(item)

            order.total = total
            db.session.add(order)
            db.session.commit()
            flash('Orden de compra creada con éxito', 'success')
            return redirect(url_for('suppliers_controller.purchase_orders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la orden de compra: {str(e)}', 'danger')

    suppliers = Supplier.query.all()
    products = Product.query.all()
    return render_template('suppliers/new_purchase_order.html', suppliers=suppliers, products=products)