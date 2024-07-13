import logging

from flask import request, app, jsonify

from app import bcrypt
from app.users import bp
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bp.route('/auth', methods=['POST'])
def authenticate_user():
    data = request.get_json()
    username = data['username'].strip()
    password = data['password'].strip()
    user_type = data['user_type']
    try:
        user = Config.users_collection.find_one({'username': username, 'user_type': user_type})
        if user and bcrypt.check_password_hash(user["password"], password):
            logger.info(f"Login success: {username}-{user_type}")
            return jsonify({"message": "login success"}), 200
        else:
            logger.error(f"Login failed: {username}-{user_type}")
            return jsonify({"message": "Incorrect Username, Password and User type combination"}), 401
    except Exception as e:
        logger.error(f"Error in users/auth {str(e)}")
        return jsonify({'message': str(e)}), 500
