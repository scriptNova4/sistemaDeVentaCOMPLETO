from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, Category, InventoryMovement, User
from app.api.products import products_bp

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Obtener lista de productos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    barcode = request.args.get('barcode')
    name = request.args.get('name')
    low_stock = request.args.get('low_stock', type=bool)

    query = Product.query

    # Aplicar filtros
    if category_id:
        query = query.filter_by(category_id=category_id)
    if barcode:
        query = query.filter_by(barcode=barcode)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    if low_stock:
        query = query.filter(Product.stock <= Product.min_stock)

    # Ordenar por nombre por defecto
    query = query.order_by(Product.name)

    # Paginar resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return jsonify({
        'items': [{
            'id': product.id,
            'barcode': product.barcode,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'cost': product.cost,
            'stock': product.stock,
            'min_stock': product.min_stock,
            'image_url': product.image_url,
            'status': product.status,
            'category_id': product.category_id,
            'profit_margin': product.profit_margin,
            'is_low_stock': product.is_low_stock
        } for product in products],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Obtener un producto por su ID"""
    product = Product.query.get_or_404(product_id)

    return jsonify({
        'id': product.id,
        'barcode': product.barcode,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'cost': product.cost,
        'tax_rate': product.tax_rate,
        'stock': product.stock,
        'min_stock': product.min_stock,
        'max_stock': product.max_stock,
        'image_url': product.image_url,
        'status': product.status,
        'category_id': product.category_id,
        'supplier_id': product.supplier_id,
        'profit_margin': product.profit_margin,
        'is_low_stock': product.is_low_stock,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    })

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Crear un nuevo producto"""
    data = request.json

    # Verificar si el código de barras ya existe
    if data.get('barcode') and Product.query.filter_by(barcode=data['barcode']).first():
        return jsonify({'error': 'El código de barras ya está registrado'}), 400

    try:
        product = Product(
            barcode=data.get('barcode'),
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            cost=data['cost'],
            tax_rate=data.get('tax_rate', 0.0),
            stock=data.get('stock', 0),
            min_stock=data.get('min_stock', 5),
            max_stock=data.get('max_stock', 100),
            image_url=data.get('image_url'),
            status=data.get('status', 'active'),
            category_id=data.get('category_id'),
            supplier_id=data.get('supplier_id')
        )

        db.session.add(product)
        db.session.commit()

        # Registrar movimiento de inventario si hay stock inicial
        if product.stock > 0:
            inventory_movement = InventoryMovement(
                product_id=product.id,
                quantity=product.stock,
                movement_type='entrada',
                reference='Stock inicial',
                user_id=get_jwt_identity()
            )
            db.session.add(inventory_movement)
            db.session.commit()

        return jsonify({
            'message': 'Producto creado con éxito',
            'product': {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'price': product.price,
                'stock': product.stock
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Actualizar un producto existente"""
    product = Product.query.get_or_404(product_id)
    data = request.json

    # Verificar si el código de barras ya existe
    if 'barcode' in data and data['barcode'] != product.barcode:
        existing_product = Product.query.filter_by(barcode=data['barcode']).first()
        if existing_product:
            return jsonify({'error': 'El código de barras ya está registrado'}), 400

    try:
        # Actualizar campos del producto
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        db.session.commit()

        return jsonify({
            'message': 'Producto actualizado con éxito',
            'product': {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'price': product.price,
                'stock': product.stock
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Eliminar un producto (cambiar status a 'discontinued')"""
    product = Product.query.get_or_404(product_id)

    try:
        product.status = 'discontinued'
        db.session.commit()

        return jsonify({'message': 'Producto descontinuado con éxito'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>/inventory', methods=['POST'])
@jwt_required()
def add_inventory(product_id):
    """Añadir stock a un producto"""
    product = Product.query.get_or_404(product_id)
    data = request.json

    quantity = data.get('quantity', 0)
    if quantity <= 0:
        return jsonify({'error': 'La cantidad debe ser mayor que cero'}), 400

    try:
        # Añadir movimiento de inventario
        inventory_movement = InventoryMovement(
            product_id=product.id,
            quantity=quantity,
            movement_type='entrada',
            reference=data.get('reference', 'Entrada manual'),
            notes=data.get('notes'),
            user_id=get_jwt_identity()
        )

        # Actualizar stock del producto
        product.stock += quantity

        db.session.add(inventory_movement)
        db.session.commit()

        return jsonify({
            'message': 'Stock actualizado con éxito',
            'new_stock': product.stock
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Obtener todas las categorías"""
    categories = Category.query.all()

    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description
    } for category in categories])

@products_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Crear una nueva categoría"""
    data = request.json

    # Verificar si la categoría ya existe
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 400

    try:
        category = Category(
            name=data['name'],
            description=data.get('description')
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'message': 'Categoría creada con éxito',
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
