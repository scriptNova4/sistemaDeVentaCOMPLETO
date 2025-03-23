from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import (
    Product, Sale, SaleItem, Customer, AIRecommendation,
    User, Category, Supplier
)
from datetime import datetime, timedelta
import json

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    """Página principal del dashboard"""
    # Obtener estadísticas para el dashboard
    today = datetime.now().date()

    # Estadísticas de ventas de hoy
    sales_today = Sale.query.filter(
        db.func.date(Sale.created_at) == today,
        Sale.payment_status == 'paid'
    ).all()

    sales_today_count = len(sales_today)
    sales_today_amount = sum(sale.total for sale in sales_today)

    # Estadísticas de productos
    products_count = Product.query.count()
    low_stock_count = Product.query.filter(Product.stock <= Product.min_stock).count()

    # Estadísticas de clientes
    customers_count = Customer.query.count()
    first_day_of_month = datetime(today.year, today.month, 1)
    new_customers = Customer.query.filter(Customer.created_at >= first_day_of_month).count()

    # Estadísticas de recomendaciones de IA
    ai_recommendations_count = AIRecommendation.query.count()
    pending_recommendations = AIRecommendation.query.filter_by(status='pending').count()

    # Obtener los últimos 7 días para el gráfico de ventas
    last_7_days = []
    sales_7_days = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_sales = db.session.query(db.func.sum(Sale.total)).filter(
            db.func.date(Sale.created_at) == day,
            Sale.payment_status == 'paid'
        ).scalar() or 0

        last_7_days.append(day.strftime('%d/%m'))
        sales_7_days.append(float(day_sales))

    # Productos más vendidos
    top_products_data = db.session.query(
        Product.id,
        Product.name,
        db.func.sum(SaleItem.quantity).label('sold_count'),
        db.func.sum(SaleItem.total).label('revenue')
    ).join(
        SaleItem, SaleItem.product_id == Product.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.created_at >= today - timedelta(days=30),
        Sale.payment_status == 'paid'
    ).group_by(
        Product.id
    ).order_by(
        db.func.sum(SaleItem.quantity).desc()
    ).limit(5).all()

    top_products = [
        {
            'name': p[1],
            'sold_count': p[2],
            'revenue': float(p[3])
        } for p in top_products_data
    ]

    # Últimas ventas
    recent_sales = db.session.query(
        Sale.ticket_number,
        Customer.name.label('customer_name'),
        Sale.total,
        Sale.created_at
    ).outerjoin(
        Customer, Customer.id == Sale.customer_id
    ).filter(
        Sale.payment_status == 'paid'
    ).order_by(
        Sale.created_at.desc()
    ).limit(5).all()

    recent_sales_data = [
        {
            'ticket_number': s[0],
            'customer_name': s[1],
            'total': float(s[2]),
            'created_at': s[3]
        } for s in recent_sales
    ]

    # Recomendaciones recientes de IA
    ai_recommendations = AIRecommendation.query.order_by(
        AIRecommendation.created_at.desc()
    ).limit(3).all()

    return render_template(
        'index.html',
        sales_today_count=sales_today_count,
        sales_today_amount=sales_today_amount,
        products_count=products_count,
        low_stock_count=low_stock_count,
        customers_count=customers_count,
        new_customers=new_customers,
        ai_recommendations_count=ai_recommendations_count,
        pending_recommendations=pending_recommendations,
        sales_chart_labels=json.dumps(last_7_days),
        sales_chart_data=json.dumps(sales_7_days),
        top_products=top_products,
        recent_sales=recent_sales_data,
        ai_recommendations=ai_recommendations
    )
