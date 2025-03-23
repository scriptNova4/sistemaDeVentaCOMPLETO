# app/api/customers.py
from flask import Blueprint

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/test', methods=['GET'])
def test_customers():
    return {"message": "Ruta de clientes funcionando"}, 200