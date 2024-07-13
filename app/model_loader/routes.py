import importlib
import logging

from bson import ObjectId
from bson.json_util import dumps
from flask import jsonify, request

from app.model_loader import bp
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import model.Initializer

    model_configs = Config.model_collection.find_one({"status": "Active"})
    fuseNet = model.Initializer.initialize_model(model_configs)
    logger.info(f"Model loaded: {model_configs}")
except Exception as e:
    logger.error(f"Error occurred when loading model: {str(e)}")


@bp.route('/', methods=['GET'])
def index():
    try:
        records = Config.model_collection.find()
        result = []
        for record in records:
            record['_id'] = str(record['_id'])
            result.append(record)
        logger.info(f"Fetched {len(result)} model records")
        return jsonify(result[::-1]), 200
    except Exception as e:
        logger.error(f"Error in model_loader/ {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/update_model', methods=['PUT'])
def update_model():
    try:
        global fuseNet
        data = request.json.get("query")

        import model.Initializer
        model_configs = Config.model_collection.find_one({"_id": ObjectId(data["activate_id"])})
        if not model_configs:
            return jsonify({"message": "Model to activate not found"}), 404
        fuseNet = model.Initializer.initialize_model(model_configs)
        logger.info(f"Activated new model: {model_configs}")
        for key, value in data.items():
            query = {"_id": ObjectId(value)}
            status = ""
            if key == "activate_id":
                status = "Active"
            result = Config.model_collection.update_one(
                query,
                {"$set": {"status": status}}
            )
            if result.matched_count == 0:
                status_print = status.lower()
                if status == "": status_print = "deactivate"
                logger.error(f"Model to {status_print}: {value} not found")
                return jsonify({"message": "Model to " + status_print.lower() + " not found"}), 404

        logger.info(f"Model database updated")
        return jsonify({"message": "Model activate successfully"}), 200

    except Exception as e:
        logger.error(f"Error in model_loader/update_model {str(e)}")
        return jsonify({'message': str(e)}), 500


@bp.route('/get_model', methods=['GET'])
def get_active_model():
    try:
        data = request.json
        data["_id"] = ObjectId(data["_id"])
        active_model_configs = Config.model_collection.find_one(data)
        logger.info(f"Active model fetched: {active_model_configs}")
        return dumps(active_model_configs), 200
    except Exception as e:
        logger.error(f"Error in model_loader/get_model {str(e)}")
        return jsonify({'error': str(e)}), 500
