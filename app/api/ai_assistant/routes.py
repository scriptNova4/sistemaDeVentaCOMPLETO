from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import (
    AIRecommendation, AIAction, AIInsight, AIModel,
    Product, Sale, SaleItem, Customer, User
)
from app.api.ai_assistant import ai_bp
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import requests
import json
import random

@ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Obtener recomendaciones generadas por la IA"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    recommendation_type = request.args.get('type')
    status = request.args.get('status')

    query = AIRecommendation.query

    # Aplicar filtros
    if recommendation_type:
        query = query.filter_by(recommendation_type=recommendation_type)
    if status:
        query = query.filter_by(status=status)

    # Ordenar por fecha descendente
    query = query.order_by(AIRecommendation.created_at.desc())

    # Paginar resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    recommendations = pagination.items

    return jsonify({
        'items': [{
            'id': rec.id,
            'recommendation_type': rec.recommendation_type,
            'title': rec.title,
            'description': rec.description,
            'confidence': rec.confidence,
            'status': rec.status,
            'created_at': rec.created_at,
            'applied_at': rec.applied_at
        } for rec in recommendations],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@ai_bp.route('/recommendations/<int:recommendation_id>', methods=['GET'])
@jwt_required()
def get_recommendation(recommendation_id):
    """Obtener una recomendación específica con sus acciones"""
    recommendation = AIRecommendation.query.get_or_404(recommendation_id)

    actions = [{
        'id': action.id,
        'action_type': action.action_type,
        'entity_type': action.entity_type,
        'entity_id': action.entity_id,
        'value': action.value,
        'notes': action.notes,
        'status': action.status
    } for action in recommendation.actions]

    return jsonify({
        'id': recommendation.id,
        'recommendation_type': recommendation.recommendation_type,
        'title': recommendation.title,
        'description': recommendation.description,
        'confidence': recommendation.confidence,
        'status': recommendation.status,
        'created_at': recommendation.created_at,
        'applied_at': recommendation.applied_at,
        'actions': actions
    })

@ai_bp.route('/recommendations/<int:recommendation_id>/apply', methods=['PUT'])
@jwt_required()
def apply_recommendation(recommendation_id):
    """Aplicar una recomendación específica"""
    recommendation = AIRecommendation.query.get_or_404(recommendation_id)

    if recommendation.status == 'applied':
        return jsonify({'error': 'La recomendación ya ha sido aplicada'}), 400

    try:
        # Aplicar las acciones específicas según el tipo de recomendación
        for action in recommendation.actions:
            if action.entity_type == 'product':
                product = Product.query.get(action.entity_id)
                if product:
                    if action.action_type == 'adjust_price':
                        product.price = float(action.value)
                    elif action.action_type == 'adjust_min_stock':
                        product.min_stock = int(action.value)
                    # Añadir más tipos de acciones según sea necesario

            # Marcar la acción como aplicada
            action.status = 'applied'
            action.applied_at = datetime.utcnow()

        # Actualizar estado de la recomendación
        recommendation.status = 'applied'
        recommendation.applied_at = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Recomendación aplicada con éxito'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations/<int:recommendation_id>/reject', methods=['PUT'])
@jwt_required()
def reject_recommendation(recommendation_id):
    """Rechazar una recomendación específica"""
    recommendation = AIRecommendation.query.get_or_404(recommendation_id)

    if recommendation.status != 'pending':
        return jsonify({'error': f'La recomendación no está pendiente, su estado actual es: {recommendation.status}'}), 400

    try:
        # Rechazar todas las acciones
        for action in recommendation.actions:
            action.status = 'rejected'

        # Actualizar estado de la recomendación
        recommendation.status = 'rejected'

        db.session.commit()

        return jsonify({'message': 'Recomendación rechazada'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """Obtener insights generados por la IA"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    insight_type = request.args.get('type')
    is_important = request.args.get('is_important', type=bool)

    query = AIInsight.query

    # Aplicar filtros
    if insight_type:
        query = query.filter_by(insight_type=insight_type)
    if is_important is not None:
        query = query.filter_by(is_important=is_important)

    # Ordenar por fecha descendente
    query = query.order_by(AIInsight.created_at.desc())

    # Paginar resultados
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    insights = pagination.items

    return jsonify({
        'items': [{
            'id': insight.id,
            'insight_type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'is_important': insight.is_important,
            'read_status': insight.read_status,
            'created_at': insight.created_at
        } for insight in insights],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@ai_bp.route('/generate-recommendations', methods=['POST'])
@jwt_required()
def generate_recommendations():
    """Generar recomendaciones basadas en datos actuales"""
    try:
        # Generar diferentes tipos de recomendaciones
        inventory_recommendations = generate_inventory_recommendations()
        pricing_recommendations = generate_pricing_recommendations()
        marketing_recommendations = generate_marketing_recommendations()

        # Combinar todas las recomendaciones
        all_recommendations = inventory_recommendations + pricing_recommendations + marketing_recommendations

        return jsonify({
            'message': f'Se generaron {len(all_recommendations)} recomendaciones con éxito',
            'recommendations': [{
                'id': rec.id,
                'recommendation_type': rec.recommendation_type,
                'title': rec.title,
                'confidence': rec.confidence
            } for rec in all_recommendations]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_inventory_recommendations():
    """Generar recomendaciones de inventario"""
    recommendations = []

    # Obtener productos con bajo stock
    low_stock_products = Product.query.filter(Product.stock <= Product.min_stock).all()

    if low_stock_products:
        # Crear recomendación general
        recommendation = AIRecommendation(
            recommendation_type='inventory',
            title=f'Reordenar {len(low_stock_products)} productos con bajo stock',
            description=f'Se han identificado {len(low_stock_products)} productos que están por debajo del nivel mínimo de stock.',
            confidence=0.9
        )
        db.session.add(recommendation)
        db.session.commit()

        # Crear acciones específicas para cada producto
        for product in low_stock_products:
            # Calcular cantidad a reordenar
            reorder_qty = product.max_stock - product.stock

            action = AIAction(
                recommendation_id=recommendation.id,
                action_type='reorder',
                entity_type='product',
                entity_id=product.id,
                value=str(reorder_qty),
                notes=f'Stock actual: {product.stock}, Stock mínimo: {product.min_stock}'
            )
            db.session.add(action)

        db.session.commit()
        recommendations.append(recommendation)

    # Otras recomendaciones de inventario...

    return recommendations

def generate_pricing_recommendations():
    """Generar recomendaciones de precios"""
    recommendations = []

    # Obtener productos con baja rotación pero alto margen
    # Este es un ejemplo simplificado, en un sistema real se usarían análisis más complejos
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    low_rotation_products = db.session.query(
        Product,
        db.func.count(SaleItem.id).label('sales_count')
    ).outerjoin(
        SaleItem
    ).outerjoin(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.created_at >= thirty_days_ago
    ).group_by(
        Product.id
    ).having(
        db.func.count(SaleItem.id) < 5
    ).filter(
        Product.profit_margin > 30
    ).all()

    if low_rotation_products:
        # Crear recomendación
        recommendation = AIRecommendation(
            recommendation_type='pricing',
            title=f'Ajustar precios de {len(low_rotation_products)} productos con baja rotación',
            description='Estos productos tienen un alto margen de beneficio pero baja rotación. Considere reducir el precio para aumentar las ventas.',
            confidence=0.8
        )
        db.session.add(recommendation)
        db.session.commit()

        # Crear acciones específicas
        for product, sales_count in low_rotation_products:
            # Calcular nuevo precio sugerido (reducción del 10%)
            suggested_price = round(product.price * 0.9, 2)

            action = AIAction(
                recommendation_id=recommendation.id,
                action_type='adjust_price',
                entity_type='product',
                entity_id=product.id,
                value=str(suggested_price),
                notes=f'Precio actual: {product.price}, Ventas últimos 30 días: {sales_count}'
            )
            db.session.add(action)

        db.session.commit()
        recommendations.append(recommendation)

    return recommendations

def generate_marketing_recommendations():
    """Generar recomendaciones de marketing"""
    recommendations = []

    # Ejemplo: Recomendar promociones para productos populares
    # Este es un ejemplo simplificado
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    popular_products = db.session.query(
        Product,
        db.func.sum(SaleItem.quantity).label('total_sold')
    ).join(
        SaleItem
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.created_at >= thirty_days_ago
    ).group_by(
        Product.id
    ).order_by(
        db.func.sum(SaleItem.quantity).desc()
    ).limit(5).all()

    if popular_products:
        # Crear recomendación
        recommendation = AIRecommendation(
            recommendation_type='marketing',
            title=f'Campaña de promoción para los {len(popular_products)} productos más vendidos',
            description='Aproveche la popularidad de estos productos con una promoción especial para aumentar las ventas cruzadas.',
            confidence=0.75
        )
        db.session.add(recommendation)
        db.session.commit()

        # Crear acciones específicas
        for product, total_sold in popular_products:
            action = AIAction(
                recommendation_id=recommendation.id,
                action_type='promotion',
                entity_type='product',
                entity_id=product.id,
                value='featured',
                notes=f'Total vendido en los últimos 30 días: {total_sold}'
            )
            db.session.add(action)

        db.session.commit()
        recommendations.append(recommendation)

    return recommendations

@ai_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_data():
    """Analizar datos y generar insights"""
    try:
        # Ejemplo de generación de insights en ventas
        sales_trend_insight = analyze_sales_trends()

        # Ejemplo de segmentación de clientes
        customer_segments_insight = segment_customers()

        # Devolver resultados
        insights = []
        if sales_trend_insight:
            insights.append({
                'id': sales_trend_insight.id,
                'insight_type': sales_trend_insight.insight_type,
                'title': sales_trend_insight.title
            })

        if customer_segments_insight:
            insights.append({
                'id': customer_segments_insight.id,
                'insight_type': customer_segments_insight.insight_type,
                'title': customer_segments_insight.title
            })

        return jsonify({
            'message': f'Se generaron {len(insights)} insights',
            'insights': insights
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_sales_trends():
    """Analizar tendencias de ventas"""
    # Este es un ejemplo simplificado, en un sistema real se usarían algoritmos más sofisticados

    # Obtener ventas de los últimos 90 días agrupadas por día
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)

    daily_sales = db.session.query(
        db.func.date(Sale.created_at).label('date'),
        db.func.sum(Sale.total).label('total_sales')
    ).filter(
        Sale.created_at >= ninety_days_ago,
        Sale.payment_status == 'paid'
    ).group_by(
        db.func.date(Sale.created_at)
    ).order_by(
        db.func.date(Sale.created_at)
    ).all()

    if not daily_sales:
        return None

    # Convertir a DataFrame para análisis
    df = pd.DataFrame(daily_sales, columns=['date', 'total_sales'])

    # Calcular promedio, tendencia, etc.
    avg_daily_sales = df['total_sales'].mean()
    recent_avg = df['total_sales'].tail(10).mean()

    is_improving = recent_avg > avg_daily_sales
    change_percent = ((recent_avg / avg_daily_sales) - 1) * 100 if avg_daily_sales > 0 else 0

    # Crear insight
    insight = AIInsight(
        insight_type='sales_trend',
        title=f'Las ventas están {"mejorando" if is_improving else "disminuyendo"}',
        description=f'Las ventas diarias promedio son {avg_daily_sales:.2f}. En los últimos 10 días, el promedio es {recent_avg:.2f}, lo que representa un {"aumento" if is_improving else "descenso"} del {abs(change_percent):.1f}%.',
        data=json.dumps({
            'dates': [str(d[0]) for d in daily_sales],
            'values': [float(d[1]) for d in daily_sales],
            'avg_daily_sales': float(avg_daily_sales),
            'recent_avg': float(recent_avg),
            'change_percent': float(change_percent)
        }),
        is_important=abs(change_percent) > 10  # Marcar como importante si el cambio es significativo
    )

    db.session.add(insight)
    db.session.commit()

    return insight

def segment_customers():
    customer_data = db.session.query(
        Customer.id,
        db.func.count(Sale.id).label('purchase_count'),
        db.func.sum(Sale.total).label('total_spent'),
        db.func.max(Sale.created_at).label('last_purchase')
    ).outerjoin(
        Sale, Sale.customer_id == Customer.id
    ).filter(
        Customer.id.isnot(None)
    ).group_by(
        Customer.id
    ).all()

    if len(customer_data) < 3:  # Necesitamos al menos 3 clientes para segmentar
        return None

    customer_df = pd.DataFrame(customer_data, columns=['customer_id', 'purchase_count', 'total_spent', 'last_purchase'])
    now = datetime.utcnow()
    customer_df['days_since_last_purchase'] = customer_df['last_purchase'].apply(
        lambda x: (now - x).days if pd.notnull(x) else 365
    )

    X = customer_df[['purchase_count', 'total_spent', 'days_since_last_purchase']].fillna(0).values
    if len(X) < 3:
        return None

    # Normalizar datos
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0)
    X_std[X_std == 0] = 1  # Evitar división por cero
    X = (X - X_mean) / X_std

    n_clusters = min(4, len(X))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    customer_df['segment'] = kmeans.fit_predict(X)

    segment_descriptions = []
    for segment in range(n_clusters):
        segment_data = customer_df[customer_df['segment'] == segment]
        avg_purchases = segment_data['purchase_count'].mean()
        avg_spent = segment_data['total_spent'].mean()
        avg_recency = segment_data['days_since_last_purchase'].mean()

        if avg_spent > customer_df['total_spent'].mean() and avg_recency < 30:
            segment_type = "VIP"
        elif avg_recency < 30:
            segment_type = "Activo"
        elif avg_recency < 90:
            segment_type = "En riesgo"
        else:
            segment_type = "Inactivo"

        segment_descriptions.append({
            'segment': segment,
            'type': segment_type,
            'count': len(segment_data),
            'avg_purchases': float(avg_purchases),
            'avg_spent': float(avg_spent),
            'avg_recency': float(avg_recency)
        })

    insight = AIInsight(
        insight_type='customer_segmentation',
        title=f'Segmentación de {len(customer_df)} clientes en {n_clusters} grupos',
        description='Los clientes han sido segmentados basados en frecuencia de compra, gasto total y tiempo desde la última compra.',
        data=json.dumps({
            'segments': segment_descriptions,
            'segment_counts': [len(customer_df[customer_df['segment'] == i]) for i in range(n_clusters)]
        })
    )

    db.session.add(insight)
    db.session.commit()
    return insight