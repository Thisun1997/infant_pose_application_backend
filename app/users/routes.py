from flask import request, app, jsonify

from app import bcrypt
from app.users import bp
from config import Config


@bp.route('/')
def index():
    return "home"


@bp.route('/auth', methods=['POST'])
def authenticate_user():
    data = request.get_json()
    username = data['username'].strip()
    password = data['password'].strip()
    user_type = data['user_type']

    user = Config.users_collection.find_one({'username': username, 'user_type': user_type})
    if user and bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "login success"}), 200
    else:
        return jsonify({"message": "Incorrect Username, Password and User type combination"}), 401
