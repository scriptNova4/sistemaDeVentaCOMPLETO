from datetime import datetime
from app import db

class Customer(db.Model):
    """Modelo para clientes"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    tax_id = db.Column(db.String(20))  # ID fiscal, RFC, etc.
    notes = db.Column(db.Text)
    credit_limit = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    loyalty_points = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.name}>'

    @property
    def available_credit(self):
        """Calcula el crédito disponible del cliente"""
        return max(0, self.credit_limit - self.current_balance)


class LoyaltyProgram(db.Model):
    """Modelo para programa de fidelización"""
    __tablename__ = 'loyalty_programs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_per_purchase = db.Column(db.Float, nullable=False, default=1.0)
    points_to_currency = db.Column(db.Float, nullable=False, default=0.01)
    min_points_to_redeem = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LoyaltyProgram {self.name}>'


class LoyaltyTransaction(db.Model):
    """Modelo para transacciones de puntos de fidelización"""
    __tablename__ = 'loyalty_transactions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    points = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # earned, redeemed, adjusted
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    customer = db.relationship('Customer', backref='loyalty_transactions')

    def __repr__(self):
        return f'<LoyaltyTransaction {self.id}>'
