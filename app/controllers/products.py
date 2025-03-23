# app/controllers/products.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, InventoryMovement

products_controller = Blueprint('products_controller', __name__)

@products_controller.route('/products')
@login_required
def list_products():
    """Lista de productos"""
    products = Product.query.all()
    return render_template('products/list_products.html', products=products)

@products_controller.route('/products/new', methods=['GET', 'POST'])
@login_required
def new_product():
    """Crear un nuevo producto"""
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form['name'],
                barcode=request.form['barcode'],
                description=request.form.get('description'),
                price=float(request.form['price']),
                cost=float(request.form['cost']),
                stock=int(request.form.get('stock', 0)),
                min_stock=int(request.form.get('min_stock', 5)),
                max_stock=int(request.form.get('max_stock', 100)),
                category_id=request.form['category_id']
            )
            db.session.add(product)
            db.session.commit()

            if product.stock > 0:
                inventory_movement = InventoryMovement(
                    product_id=product.id,
                    quantity=product.stock,
                    movement_type='entrada',
                    reference='Stock inicial',
                    user_id=current_user.id
                )
                db.session.add(inventory_movement)
                db.session.commit()

            flash('Producto creado con éxito', 'success')
            return redirect(url_for('products_controller.list_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el producto: {str(e)}', 'danger')

    categories = Category.query.all()
    return render_template('products/new_product.html', categories=categories)

@products_controller.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Editar un producto existente"""
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.barcode = request.form['barcode']
            product.description = request.form.get('description')
            product.price = float(request.form['price'])
            product.cost = float(request.form['cost'])
            product.min_stock = int(request.form.get('min_stock', 5))
            product.max_stock = int(request.form.get('max_stock', 100))
            product.category_id = request.form['category_id']
            db.session.commit()
            flash('Producto actualizado con éxito', 'success')
            return redirect(url_for('products_controller.list_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'danger')

    categories = Category.query.all()
    return render_template('products/edit_product.html', product=product, categories=categories)

@products_controller.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Eliminar un producto"""
    product = Product.query.get_or_404(product_id)
    try:
        product.status = 'discontinued'
        db.session.commit()
        flash('Producto descontinuado con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al descontinuar el producto: {str(e)}', 'danger')
    return redirect(url_for('products_controller.list_products'))

@products_controller.route('/categories')
@login_required
def categories():
    """Lista de categorías"""
    categories = Category.query.all()
    return render_template('products/categories.html', categories=categories)

@products_controller.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """Crear una nueva categoría"""
    if request.method == 'POST':
        try:
            category = Category(
                name=request.form['name'],
                description=request.form.get('description')
            )
            db.session.add(category)
            db.session.commit()
            flash('Categoría creada con éxito', 'success')
            return redirect(url_for('products_controller.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la categoría: {str(e)}', 'danger')
    return render_template('products/new_category.html')