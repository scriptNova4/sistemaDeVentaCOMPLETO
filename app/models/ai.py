from datetime import datetime
from app import db

class AIRecommendation(db.Model):
    """Modelo para recomendaciones de IA"""
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    recommendation_type = db.Column(db.String(50), nullable=False)  # inventory, promotion, customer, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # de 0 a 1
    status = db.Column(db.String(20), default='pending')  # pending, applied, rejected
    applied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    actions = db.relationship('AIAction', backref='recommendation', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<AIRecommendation {self.title}>'


class AIAction(db.Model):
    """Modelo para acciones específicas recomendadas por la IA"""
    __tablename__ = 'ai_actions'

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('ai_recommendations.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # adjust_price, reorder, promotion, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # product, customer, category, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.String(255), nullable=False)  # valor específico de la acción (depende del tipo)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, applied, rejected
    applied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIAction {self.action_type}>'


class AIModel(db.Model):
    """Modelo para gestionar modelos de IA"""
    __tablename__ = 'ai_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # product_recommendation, sales_prediction, etc.
    description = db.Column(db.Text)
    version = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    configuration = db.Column(db.Text)  # Configuración JSON del modelo
    last_training = db.Column(db.DateTime)
    accuracy = db.Column(db.Float)  # Precisión del modelo (de 0 a 1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AIModel {self.name}>'


class AIInsight(db.Model):
    """Modelo para insights generados por la IA"""
    __tablename__ = 'ai_insights'

    id = db.Column(db.Integer, primary_key=True)
    insight_type = db.Column(db.String(50), nullable=False)  # sales_trend, customer_behavior, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text)  # Datos JSON relacionados con el insight
    is_important = db.Column(db.Boolean, default=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIInsight {self.title}>'
