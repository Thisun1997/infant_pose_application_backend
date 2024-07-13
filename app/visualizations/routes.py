import logging
from datetime import datetime, timedelta

import numpy as np
from bson import Binary, ObjectId
from bson.json_util import dumps
from flask import request, jsonify

from app.utils.preprocess import preprocess, display_output
from app.visualizations import bp
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bp.route('/prediction', methods=['POST'])
def display_prediction():
    try:
        data = request.get_json()
        depth_image = np.array(data["depth"], dtype="uint16")
        pressure_image = np.array(data["pressure"], dtype="float32")
        processed_image, image_patch = preprocess(depth_image, pressure_image)
        from app.model_loader.routes import fuseNet, model_configs
        pred = fuseNet(processed_image)
        logger.info("Prediction completed")
        output = display_output(pred, image_patch)

        data["visualization"] = Binary(output.getvalue())
        data["model_id"] = str(model_configs["_id"])
        result = Config.visualization_collection.insert_one(data)
        logger.info(f"Prediction saved: {str(result.inserted_id)}")
        return jsonify({"message": str(result.inserted_id)}), 200
    except Exception as e:
        logger.error(f"Error in visualizations/prediction {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/update', methods=['PUT'])
def update_document():
    try:
        data = request.json
        query = data.get('query')
        query["_id"] = ObjectId(query["_id"])
        new_field = data.get('new_field')

        if not query or not new_field:
            logger.info(f"Invalid visualization data to update: {data}")
            return jsonify({"message": "Invalid input"}), 400

        result = Config.visualization_collection.update_one(
            query,
            {"$set": new_field}
        )

        if result.matched_count == 0:
            logger.info(f"No visualization data found to update: {data}")
            return jsonify({"message": "Record not found"}), 404

        logger.info(f"Visualization data updated: {data}")
        return jsonify({"message": "Record updated successfully"}), 200

    except Exception as e:
        logger.error(f"Error in visualizations/update {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/visualization_data', methods=['GET'])
def get_visualization_data():
    data = request.get_json()
    data["_id"] = ObjectId(data["_id"])
    try:
        data = Config.visualization_collection.find_one(data)
        logger.info(f"Visualization data fetched: {str(data['_id'])}")
        return dumps(data), 200
    except Exception as e:
        logger.error(f"Error in visualizations/visualization_data {str(e)}")
        return jsonify({"message": str(e)}), 500


@bp.route('/history_data', methods=['GET'])
def get_history_data():
    data = request.get_json()
    datetime_format = "%Y-%m-%d"
    start_time = int(datetime.strptime(data["from_time"], datetime_format).timestamp() * 1e9)
    end_time = int((datetime.strptime(data["to_time"], datetime_format) + timedelta(days=1) - timedelta(
        microseconds=1)).timestamp() * 1e9)
    try:
        if end_time <= start_time:
            return jsonify({"message": "Time range is invalid"}), 400
        data = Config.visualization_collection.find({
            "time": {"$gte": start_time, "$lte": end_time},
            "patient_id": int(data["patient_id"])
        })
        data_list = list(data)[::-1]
        if len(data_list) == 0:
            logger.info(f"No historical Visualization data: {data}")
            return jsonify({"message": "No historical data available"}), 400
        logger.info(f"Fetched {len(data_list)} historical Visualization data")
        return dumps(data_list), 200
    except Exception as e:
        logger.error(f"Error in visualizations/history_data {str(e)}")
        return jsonify({"message": str(e)}), 500
