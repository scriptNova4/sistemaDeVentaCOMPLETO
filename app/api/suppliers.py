# app/api/suppliers.py
from flask import Blueprint

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/test', methods=['GET'])
def test_suppliers():
    return {"message": "Ruta de proveedores funcionando"}, 200