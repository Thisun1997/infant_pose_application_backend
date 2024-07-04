from flask import Blueprint

bp = Blueprint('visualizations', __name__)

from app.visualizations import routes