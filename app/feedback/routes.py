import logging

from flask import request, jsonify

from app.feedback import bp
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/', methods=["GET"])
def index():
    try:
        records = Config.feedback_collection.find()
        result = []
        for record in records:
            record['_id'] = str(record['_id'])
            result.append(record)
        logger.info(f"Fetched {len(result)} Feedback records")
        return jsonify(result[::-1]), 200
    except Exception as e:
        logger.error(f"Error in feedback/ {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/add', methods=['POST'])
def add_feedback():
    data = request.get_json()
    try:
        Config.feedback_collection.insert_one(data)
        logger.info(f"Feedback inserted: {data}")
        return jsonify({"message": "feedback submitted successfully"}), 200
    except Exception as e:
        logger.error(f"Error in feedback/add/ {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/get', methods=['GET'])
def get_feedback():
    data = request.get_json()
    try:
        response = Config.feedback_collection.find_one(data)
        logger.info(f"Feedback fetched: {response}")
        if response:
            return jsonify({"message": response["feedback"]}), 200
        else:
            return jsonify({"message": "-"}), 404
    except Exception as e:
        logger.error(f"Error in feedback/get/ {str(e)}")
        return jsonify({"message": str(e)}), 500
