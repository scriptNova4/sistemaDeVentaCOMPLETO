from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Sale, SaleItem, Payment, Product, Customer, InventoryMovement
from app.api.sales import sales_bp
from datetime import datetime
import uuid

def generate_ticket_number():
    """Generar un número de ticket único"""
    date_str = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4().int)[:6]
    return f"T{date_str}{unique_id}"

@sales_bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    """Obtener lista de ventas"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    customer_id = request.args.get('customer_id', type=int)
    payment_status = request.args.get('payment_status')

    query = Sale.query

    # Aplicar filtros
    if start_date:
        query = query.filter(Sale.created_at >= start_date)
    if end_date:
        query = query.filter(Sale.created_at <= end_date)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if payment_status:
        query = query.filter_by(payment_status=payment_status)

    # Ordenar por fecha descendente
    query = query.order_by(Sale.created_at.desc())

    # Paginar resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sales = pagination.items

    return jsonify({
        'items': [{
            'id': sale.id,
            'ticket_number': sale.ticket_number,
            'customer_id': sale.customer_id,
            'customer_name': sale.customer.name if sale.customer else None,
            'user_id': sale.user_id,
            'subtotal': sale.subtotal,
            'tax_amount': sale.tax_amount,
            'discount_amount': sale.discount_amount,
            'total': sale.total,
            'payment_method': sale.payment_method,
            'payment_status': sale.payment_status,
            'created_at': sale.created_at
        } for sale in sales],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@sales_bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """Obtener una venta por su ID"""
    sale = Sale.query.get_or_404(sale_id)

    # Obtener items de la venta
    items = []
    for item in sale.items:
        product = Product.query.get(item.product_id)
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': product.name if product else 'Producto desconocido',
            'quantity': item.quantity,
            'price': item.price,
            'tax_rate': item.tax_rate,
            'discount_percent': item.discount_percent,
            'total': item.total
        })

    # Obtener pagos
    payments = [{
        'id': payment.id,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
        'reference': payment.reference,
        'created_at': payment.created_at
    } for payment in sale.payments]

    return jsonify({
        'id': sale.id,
        'ticket_number': sale.ticket_number,
        'customer_id': sale.customer_id,
        'customer_name': sale.customer.name if sale.customer else None,
        'user_id': sale.user_id,
        'subtotal': sale.subtotal,
        'tax_amount': sale.tax_amount,
        'discount_amount': sale.discount_amount,
        'total': sale.total,
        'payment_method': sale.payment_method,
        'payment_status': sale.payment_status,
        'notes': sale.notes,
        'created_at': sale.created_at,
        'items': items,
        'payments': payments
    })

@sales_bp.route('/', methods=['POST'])
@jwt_required()
def create_sale():
    """Crear una nueva venta"""
    data = request.json
    current_user_id = get_jwt_identity()

    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'La venta debe tener al menos un producto'}), 400

    try:
        # Validar productos y calcular totales
        subtotal = 0
        tax_amount = 0
        items_data = []

        for item in data['items']:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'error': f'Producto no encontrado (ID: {item["product_id"]})'}), 404

            if product.stock < item['quantity']:
                return jsonify({'error': f'Stock insuficiente para {product.name}'}), 400

            # Calcular precio total del item
            price = item.get('price', product.price)
            quantity = item['quantity']
            tax_rate = item.get('tax_rate', product.tax_rate)
            discount_percent = item.get('discount_percent', 0)

            # Aplicar descuento
            price_after_discount = price * (1 - discount_percent / 100)
            item_subtotal = price_after_discount * quantity
            item_tax = item_subtotal * tax_rate
            item_total = item_subtotal + item_tax

            subtotal += item_subtotal
            tax_amount += item_tax

            items_data.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': price,
                'tax_rate': tax_rate,
                'discount_percent': discount_percent,
                'total': item_total
            })

        # Aplicar descuento global si existe
        discount_amount = data.get('discount_amount', 0)
        total = subtotal + tax_amount - discount_amount

        # Crear la venta
        sale = Sale(
            ticket_number=generate_ticket_number(),
            customer_id=data.get('customer_id'),
            user_id=current_user_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total=total,
            payment_method=data['payment_method'],
            payment_status=data.get('payment_status', 'paid'),
            notes=data.get('notes')
        )

        db.session.add(sale)
        db.session.commit()

        # Crear los items de la venta
        for item_data in items_data:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                tax_rate=item_data['tax_rate'],
                discount_percent=item_data['discount_percent'],
                total=item_data['total']
            )
            db.session.add(sale_item)

            # Actualizar stock del producto
            product = Product.query.get(item_data['product_id'])
            product.stock -= item_data['quantity']

            # Registrar movimiento de inventario
            inventory_movement = InventoryMovement(
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                movement_type='salida',
                reference=f'Venta {sale.ticket_number}',
                user_id=current_user_id
            )
            db.session.add(inventory_movement)

        # Registrar el pago
        payment = Payment(
            sale_id=sale.id,
            amount=total,
            payment_method=data['payment_method'],
            reference=data.get('payment_reference')
        )
        db.session.add(payment)

        # Actualizar saldo del cliente si es venta a crédito
        if data['payment_method'] == 'credit' and sale.customer_id:
            customer = Customer.query.get(sale.customer_id)
            if customer:
                customer.current_balance += total

        db.session.commit()

        return jsonify({
            'message': 'Venta registrada con éxito',
            'sale': {
                'id': sale.id,
                'ticket_number': sale.ticket_number,
                'total': sale.total
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/<int:sale_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_sale(sale_id):
    """Cancelar una venta"""
    sale = Sale.query.get_or_404(sale_id)
    current_user_id = get_jwt_identity()

    if sale.payment_status == 'cancelled':
        return jsonify({'error': 'La venta ya ha sido cancelada'}), 400

    try:
        # Devolver productos al inventario
        for item in sale.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity

                # Registrar movimiento de inventario
                inventory_movement = InventoryMovement(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    movement_type='entrada',
                    reference=f'Cancelación venta {sale.ticket_number}',
                    user_id=current_user_id
                )
                db.session.add(inventory_movement)

        # Actualizar estado de la venta
        sale.payment_status = 'cancelled'

        # Actualizar saldo del cliente si era venta a crédito
        if sale.payment_method == 'credit' and sale.customer_id:
            customer = Customer.query.get(sale.customer_id)
            if customer:
                customer.current_balance -= sale.total

        db.session.commit()

        return jsonify({'message': 'Venta cancelada con éxito'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
