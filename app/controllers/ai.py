# app/controllers/ai.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import AIRecommendation, AIAction, AIInsight

ai_controller = Blueprint('ai_controller', __name__)

@ai_controller.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del asistente de IA"""
    recommendations = AIRecommendation.query.order_by(AIRecommendation.created_at.desc()).limit(10).all()
    insights = AIInsight.query.order_by(AIInsight.created_at.desc()).limit(10).all()
    return render_template('ai/dashboard.html', recommendations=recommendations, insights=insights)

@ai_controller.route('/recommendations/<int:rec_id>')
@login_required
def view_recommendation(rec_id):
    """Ver una recomendación específica"""
    recommendation = AIRecommendation.query.get_or_404(rec_id)
    return render_template('ai/recommendation.html', recommendation=recommendation)

@ai_controller.route('/recommendations/<int:rec_id>/apply', methods=['POST'])
@login_required
def apply_recommendation(rec_id):
    """Aplicar una recomendación"""
    recommendation = AIRecommendation.query.get_or_404(rec_id)
    if recommendation.status == 'applied':
        flash('La recomendación ya ha sido aplicada', 'danger')
        return redirect(url_for('ai_controller.view_recommendation', rec_id=rec_id))

    try:
        for action in recommendation.actions:
            if action.entity_type == 'product':
                product = Product.query.get(action.entity_id)
                if product:
                    if action.action_type == 'adjust_price':
                        product.price = float(action.value)
                    elif action.action_type == 'adjust_min_stock':
                        product.min_stock = int(action.value)
                    action.status = 'applied'
                    action.applied_at = datetime.utcnow()

        recommendation.status = 'applied'
        recommendation.applied_at = datetime.utcnow()
        db.session.commit()
        flash('Recomendación aplicada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al aplicar la recomendación: {str(e)}', 'danger')
    return redirect(url_for('ai_controller.view_recommendation', rec_id=rec_id))

@ai_controller.route('/recommendations/<int:rec_id>/reject', methods=['POST'])
@login_required
def reject_recommendation(rec_id):
    """Rechazar una recomendación"""
    recommendation = AIRecommendation.query.get_or_404(rec_id)
    if recommendation.status != 'pending':
        flash(f'La recomendación no está pendiente, su estado actual es: {recommendation.status}', 'danger')
        return redirect(url_for('ai_controller.view_recommendation', rec_id=rec_id))

    try:
        for action in recommendation.actions:
            action.status = 'rejected'
        recommendation.status = 'rejected'
        db.session.commit()
        flash('Recomendación rechazada', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al rechazar la recomendación: {str(e)}', 'danger')
    return redirect(url_for('ai_controller.view_recommendation', rec_id=rec_id))

@ai_controller.route('/insights/<int:insight_id>')
@login_required
def view_insight(insight_id):
    """Ver un insight específico"""
    insight = AIInsight.query.get_or_404(insight_id)
    insight.read_status = True
    db.session.commit()
    return render_template('ai/insight.html', insight=insight)