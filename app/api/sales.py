# app/api/sales.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.user import User
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/new_sale', methods=['POST'])
@jwt_required()
def new_sale():
    """Crear una nueva venta"""
    data = request.json

    # Obtener el usuario autenticado
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    customer_id = data.get('customer_id')
    items = data.get('items')  # Lista de ítems de la venta

    if not items:
        return jsonify({'error': 'La venta debe incluir al menos un ítem'}), 400

    # Crear la venta
    sale = Sale(
        ticket_number=f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        user_id=user_id,
        customer_id=customer_id,
        subtotal=0,  # Se calculará después
        tax_amount=0,  # Ajusta según tu lógica de impuestos
        total=0,  # Se calculará después
        payment_method=data.get('payment_method', 'cash'),
        payment_status='pending',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    subtotal = 0
    tax_amount = 0
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': f'Producto con ID {product_id} no encontrado'}), 404

        if product.stock < quantity:
            return jsonify({'error': f'Stock insuficiente para el producto {product.name}'}), 400

        # Calcular el precio del ítem
        unit_price = product.price
        item_total = unit_price * quantity
        item_tax = item_total * 0.16  # Suponiendo un IVA del 16%, ajusta según tu lógica

        # Crear ítem de la venta
        sale_item = SaleItem(
            sale=sale,
            product_id=product_id,
            quantity=quantity,
            price=unit_price,
            tax_rate=0.16,  # Ajusta según tu lógica
            total=item_total + item_tax
        )

        subtotal += item_total
        tax_amount += item_tax
        product.stock -= quantity  # Reducir el stock

        db.session.add(sale_item)

    sale.subtotal = subtotal
    sale.tax_amount = tax_amount
    sale.total = subtotal + tax_amount
    sale.payment_status = 'paid'  # Suponiendo que la venta se paga inmediatamente
    db.session.add(sale)
    db.session.commit()

    return jsonify({
        'message': 'Venta creada con éxito',
        'sale': {
            'id': sale.id,
            'ticket_number': sale.ticket_number,
            'total': sale.total,
            'created_at': sale.created_at
        }
    }), 201

@sales_bp.route('/get_sale/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """Obtener los detalles de una venta"""
    sale = Sale.query.get_or_404(sale_id)
    return jsonify({
        'id': sale.id,
        'ticket_number': sale.ticket_number,
        'total': sale.total,
        'created_at': sale.created_at
    })