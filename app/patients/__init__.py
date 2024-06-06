from flask import Blueprint

bp = Blueprint('patients', __name__)

import model.Initializer
fuseNet = model.Initializer.initialize_model()

from app.patients import routes
