# app/controllers/reports.py
from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models import Sale, Product, SaleItem, Customer, Return
from datetime import datetime, timedelta

reports_controller = Blueprint('reports_controller', __name__)

@reports_controller.route('/sales')
@login_required
def sales():
    """Reporte de ventas"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sales = Sale.query.filter(Sale.created_at >= thirty_days_ago).order_by(Sale.created_at.desc()).all()
    return render_template('reports/sales.html', sales=sales)

@reports_controller.route('/inventory')
@login_required
def inventory():
    """Reporte de inventario"""
    products = Product.query.all()
    return render_template('reports/inventory.html', products=products)

@reports_controller.route('/customers')
@login_required
def customers():
    """Reporte de clientes"""
    customers = Customer.query.all()
    return render_template('reports/customers.html', customers=customers)

@reports_controller.route('/financial')
@login_required
def financial():
    """Reporte financiero"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_sales = db.session.query(db.func.sum(Sale.total)).filter(
        Sale.created_at >= thirty_days_ago,
        Sale.payment_status == 'paid'
    ).scalar() or 0
    total_refunded = db.session.query(db.func.sum(Return.refund_amount)).filter(
        Return.created_at >= thirty_days_ago
    ).scalar() or 0
    return render_template('reports/financial.html', total_sales=total_sales, total_refunded=total_refunded)