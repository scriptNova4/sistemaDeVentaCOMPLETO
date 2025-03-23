# app/controllers/sales.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.sale import Sale, SaleItem, Return, ReturnItem
from app.models.product import Product
from app.models.customer import Customer
from datetime import datetime

sales_controller = Blueprint('sales_controller', __name__)

@sales_controller.route('/new_sale', methods=['GET', 'POST'])
@login_required
def new_sale():
    """Formulario para crear una nueva venta"""
    if request.method == 'POST':
        action = request.form.get('action')
        customer_id = request.form.get('customer_id', None)

        if action == 'add_item':
            product_id = request.form.get('product_id')
            quantity = int(request.form.get('quantity', 0))

            if not product_id or quantity <= 0:
                flash('Producto y cantidad son requeridos', 'danger')
                return redirect(url_for('sales_controller.new_sale'))

            product = Product.query.get(product_id)
            if not product:
                flash(f'Producto con ID {product_id} no encontrado', 'danger')
                return redirect(url_for('sales_controller.new_sale'))

            if product.stock < quantity:
                flash(f'Stock insuficiente para el producto {product.name}', 'danger')
                return redirect(url_for('sales_controller.new_sale'))

            # Inicializar el carrito en la sesión si no existe
            if 'cart' not in session:
                session['cart'] = []

            # Agregar el producto al carrito
            cart_item = {
                'product_id': product_id,
                'quantity': quantity,
                'name': product.name,
                'price': product.price,
                'tax_rate': 0.16,
                'total': (product.price * quantity) * (1 + 0.16)
            }
            session['cart'].append(cart_item)
            session.modified = True
            flash(f'{product.name} agregado al carrito', 'success')
            return redirect(url_for('sales_controller.new_sale'))

        elif action == 'finalize_sale':
            if 'cart' not in session or not session['cart']:
                flash('El carrito está vacío', 'danger')
                return redirect(url_for('sales_controller.new_sale'))

            # Crear la venta
            sale = Sale(
                ticket_number=f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=current_user.id,
                customer_id=customer_id if customer_id else None,
                subtotal=0,
                tax_amount=0,
                total=0,
                payment_method=request.form.get('payment_method', 'cash'),
                payment_status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            subtotal = 0
            tax_amount = 0
            for item in session['cart']:
                product = Product.query.get(item['product_id'])
                sale_item = SaleItem(
                    sale=sale,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=item['price'],
                    tax_rate=item['tax_rate'],
                    total=item['total']
                )
                subtotal += item['price'] * item['quantity']
                tax_amount += (item['price'] * item['quantity']) * item['tax_rate']
                product.stock -= item['quantity']
                db.session.add(sale_item)

            sale.subtotal = subtotal
            sale.tax_amount = tax_amount
            sale.total = subtotal + tax_amount
            sale.payment_status = 'paid'

            db.session.add(sale)
            db.session.commit()

            # Limpiar el carrito
            session.pop('cart', None)
            flash('Venta creada con éxito', 'success')
            return redirect(url_for('main.index'))

    products = Product.query.all()
    customers = Customer.query.all()
    cart = session.get('cart', [])
    return render_template('sales/new_sale.html', products=products, customers=customers, cart=cart)

@sales_controller.route('/list_sales')
@login_required
def list_sales():
    """Lista de ventas"""
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('sales/list_sales.html', sales=sales)

@sales_controller.route('/returns', methods=['GET', 'POST'])
@login_required
def returns():
    """Formulario para gestionar devoluciones"""
    if request.method == 'POST':
        sale_id = request.form.get('sale_id')
        reason = request.form.get('reason')
        refund_amount = float(request.form.get('refund_amount', 0))
        refund_method = request.form.get('refund_method', 'cash')

        sale = Sale.query.get(sale_id)
        if not sale:
            flash('Venta no encontrada', 'danger')
            return redirect(url_for('sales_controller.returns'))

        try:
            # Crear devolución
            return_obj = Return(
                sale_id=sale.id,
                user_id=current_user.id,
                reason=reason,
                refund_amount=refund_amount,
                refund_method=refund_method,
                status='processed',
                created_at=datetime.utcnow()
            )
            db.session.add(return_obj)
            db.session.commit()  # Guardar return_obj para obtener su ID

            # Devolver el stock de los productos
            for item in sale.items:
                product = Product.query.get(item.product_id)
                product.stock += item.quantity
                return_item = ReturnItem(
                    return_id=return_obj.id,  # Ahora return_obj.id está disponible
                    sale_item_id=item.id,
                    quantity=item.quantity,
                    refund_amount=item.total
                )
                db.session.add(return_item)

            sale.payment_status = 'refunded'
            db.session.commit()

            flash('Devolución procesada con éxito', 'success')
            return redirect(url_for('sales_controller.list_sales'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar la devolución: {str(e)}', 'danger')
            return redirect(url_for('sales_controller.returns'))

    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('sales/returns.html', sales=sales)