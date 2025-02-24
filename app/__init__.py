from flask import Flask

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Initialize Flask extensions here

# Register blueprints here
# from app.main import bp as main_bp
#
# app.register_blueprint(main_bp)

from app.model_loader import bp as model_loader_bp

app.register_blueprint(model_loader_bp, url_prefix='/model_loader')

from app.patients import bp as patients_bp

app.register_blueprint(patients_bp, url_prefix='/patients')

from app.users import bp as users_bp

app.register_blueprint(users_bp, url_prefix='/users')

from app.feedback import bp as feedback_bp

app.register_blueprint(feedback_bp, url_prefix='/feedback')

from app.visualizations import bp as visualization_bp

app.register_blueprint(visualization_bp, url_prefix='/visualizations')

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
#     from flask_bcrypt import Bcrypt
#     bcrypt = Bcrypt(app)
#
#     # Initialize Flask extensions here
#
#     # Register blueprints here
#     from app.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
#     from app.patients import bp as patients_bp
#     app.register_blueprint(patients_bp, url_prefix='/patients')
#
#     from app.users import bp as users_bp
#     app.register_blueprint(users_bp, url_prefix='/users')
#
#     from app.feedback import bp as feedback_bp
#     app.register_blueprint(feedback_bp, url_prefix='/feedback')
#
#     @app.route('/test/')
#     def test_page():
#         return '<h1>Testing the Flask Application Factory Pattern</h1>'
#
#     return app
