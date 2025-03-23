# app/api/inventory.py
from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/test', methods=['GET'])
def test_inventory():
    return {"message": "Ruta de inventario funcionando"}, 200