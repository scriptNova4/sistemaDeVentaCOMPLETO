from datetime import datetime
from app import db

class Category(db.Model):
    """Modelo para categorías de productos"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Modelo para productos"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(30), unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    max_stock = db.Column(db.Integer, default=100)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # active, discontinued, etc.
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sales_items = db.relationship('SaleItem', backref='product', lazy='dynamic')
    inventory_movements = db.relationship('InventoryMovement', backref='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def profit_margin(self):
        """Calcula el margen de beneficio del producto"""
        if self.cost <= 0:
            return 0
        return ((self.price - self.cost) / self.cost) * 100

    @property
    def is_low_stock(self):
        """Indica si el producto tiene stock bajo"""
        return self.stock <= self.min_stock


class InventoryMovement(db.Model):
    """Modelo para movimientos de inventario"""
    __tablename__ = 'inventory_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste, etc.
    reference = db.Column(db.String(50))  # número de factura, orden, etc.
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<InventoryMovement {self.id} - {self.movement_type}>'
