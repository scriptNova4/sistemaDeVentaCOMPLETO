# app/api/reports.py
from flask import Blueprint

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/test', methods=['GET'])
def test_reports():
    return {"message": "Ruta de reportes funcionando"}, 200