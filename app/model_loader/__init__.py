from flask import Blueprint

bp = Blueprint('model_loader', __name__)

from app.model_loader import routes
