from flask import Blueprint

products_bp = Blueprint('products', __name__)

from app.api.products import routes
