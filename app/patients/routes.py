import logging
from datetime import datetime

from bson.json_util import dumps

from flask import request, jsonify

from app.utils import utils
from app.patients import bp
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bp.route('/')
def index():
    try:
        records = Config.patients_collection.find({}, {'_id': 1, 'patient_name': 1})
        result = list(records)
        logger.info(f"Fetched {len(result)} patient records")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in patients/ {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/registration', methods=['POST'])
def register_patient():
    data = request.get_json()
    data["date_of_birth"] = datetime.combine(datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date(),
                                             datetime.min.time())
    data["_id"] = utils.get_next_sequence("document_id")
    try:
        Config.patients_collection.insert_one(data)
        logger.info(f"Patient registered: {data}")
        return jsonify({"message": "Registration successful!. Patient registration number is " + str(data["_id"])}), 200
    except Exception as e:
        logger.error(f"Error in patients/registration {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/data', methods=['GET'])
def get_patient():
    data = request.get_json()
    try:
        data = Config.patients_collection.find_one(data)
        logger.info(f"Patient fetched: {data}")
        return dumps(data), 200
    except Exception as e:
        logger.error(f"Error in patients/data {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/update_data', methods=['PUT'])
def update_patient_document():
    try:
        data = request.json
        query = data.get('query')
        query["_id"] = int(query["_id"])
        new_field = data.get('new_field')

        if not query or not new_field:
            logger.error(f"Invalid patient data to update: {data}")
            return jsonify({"message": "Invalid input"}), 400

        result = Config.patients_collection.update_one(
            query,
            {"$set": new_field}
        )

        if result.matched_count == 0:
            logger.error(f"No patient record found to update: {data}")
            return jsonify({"message": "Record not found"}), 404

        logger.info(f"Patient updated: {data}")
        return jsonify({"message": "Record updated successfully"}), 200

    except Exception as e:
        logger.error(f"Error in patients/update_data {str(e)}")
        return jsonify({"message": str(e)}), 500
