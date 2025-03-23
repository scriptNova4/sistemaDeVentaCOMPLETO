# app/api/employees.py
from flask import Blueprint

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/test', methods=['GET'])
def test_employees():
    return {"message": "Ruta de empleados funcionando"}, 200