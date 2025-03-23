from flask import Blueprint

ai_bp = Blueprint('ai_assistant', __name__)

from app.api.ai_assistant import routes
