# app/models/sale.py
from datetime import datetime
from app import db

class Sale(db.Model):
    """Modelo para ventas"""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, index=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, credit, etc.
    payment_status = db.Column(db.String(20), default='paid')  # paid, pending, cancelled, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    items = db.relationship('SaleItem', backref='sale', cascade='all, delete-orphan', lazy='dynamic')
    payments = db.relationship('Payment', backref='sale', cascade='all, delete-orphan', lazy='dynamic')
    returns = db.relationship('Return', backref='sale', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Sale {self.ticket_number}>'


class SaleItem(db.Model):
    """Modelo para items de venta"""
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<SaleItem {self.id}>'


class Payment(db.Model):
    """Modelo para pagos de ventas"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, etc.
    reference = db.Column(db.String(50))  # referencia de tarjeta, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.id}>'


class Return(db.Model):
    """Modelo para devoluciones"""
    __tablename__ = 'returns'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    refund_method = db.Column(db.String(20), nullable=False)  # cash, card, credit, etc.
    status = db.Column(db.String(20), default='processed')  # processed, pending, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    items = db.relationship('ReturnItem', backref='return_obj', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Return {self.id}>'


class ReturnItem(db.Model):
    """Modelo para items de devolución"""
    __tablename__ = 'return_items'

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('returns.id'), nullable=False)
    sale_item_id = db.Column(db.Integer, db.ForeignKey('sale_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<ReturnItem {self.id}>'