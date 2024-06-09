from datetime import datetime, timedelta

import torchvision.transforms as transforms
import cv2
from bson import Binary, ObjectId
from bson.json_util import dumps

import io
import numpy as np
from flask import Response, request, jsonify, send_file
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import utils
from app.patients import bp, fuseNet
from app.utils.preprocess import generate_patch_image, adj_bb, preprocess, display_output
from config import Config


@bp.route('/')
def index():
    try:
        records = Config.patients_collection.find({}, {'_id': 1, 'patient_name': 1})
        result = list(records)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/prediction', methods=['POST'])
def display_prediction():
    try:
        data = request.get_json()
        depth_image = np.array(data["depth"], dtype="uint16")
        pressure_image = np.array(data["pressure"], dtype="float32")
        processed_image, image_patch = preprocess(depth_image, pressure_image)
        pred = fuseNet(processed_image)
        output = display_output(pred, image_patch)

        data["visualization"] = Binary(output.getvalue())
        result = Config.visualization_collection.insert_one(data)

        return jsonify({"message": str(result.inserted_id)}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bp.route('/registration', methods=['POST'])
def register_patient():
    data = request.get_json()
    data["date_of_birth"] = datetime.combine(datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date(),
                                             datetime.min.time())
    data["_id"] = utils.get_next_sequence("document_id")
    try:
        Config.patients_collection.insert_one(data)
        return jsonify({"message": "Registration successful!. Patient registration number is " + str(data["_id"])}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bp.route('/data', methods=['GET'])
def get_patient():
    data = request.get_json()
    try:
        data = Config.patients_collection.find_one(data)
        print(data)
        return dumps(data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bp.route('/admission', methods=['POST'])
def admit_patient():
    data = request.get_json()
    try:
        Config.admissions_collection.insert_one(data)
        return jsonify({"message": "completed"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bp.route('/update', methods=['PUT'])
def update_document():
    try:
        data = request.json
        query = data.get('query')
        query["_id"] = ObjectId(query["_id"])
        new_field = data.get('new_field')
        print(data)

        if not query or not new_field:
            return jsonify({"error": "Invalid input"}), 400

        result = Config.visualization_collection.update_one(
            query,
            {"$set": new_field}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Record not found"}), 404

        return jsonify({"message": "Record updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/visualization_data', methods=['GET'])
def get_visualization_data():
    data = request.get_json()
    data["_id"] = ObjectId(data["_id"])
    try:
        data = Config.visualization_collection.find_one(data)
        return dumps(data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@bp.route('/history_data', methods=['GET'])
def get_history_data():
    data = request.get_json()
    datetime_format = "%Y-%m-%d"
    start_time = int(datetime.strptime(data["from_time"], datetime_format).timestamp()*1e9)
    end_time = int((datetime.strptime(data["to_time"], datetime_format) + timedelta(days=1) - timedelta(microseconds=1)).timestamp()*1e9)
    print(start_time, end_time)
    try:
        if end_time <= start_time:
            return jsonify({"message": "Time range is invalid"}), 400
        data = Config.visualization_collection.find({
            "time": {"$gte": start_time, "$lte": end_time},
            "patient_id": int(data["patient_id"])
        })
        data_list = list(data)[::-1]
        if len(data_list) == 0:
            return jsonify({"message": "No historical data available"}), 400
        print(len(data_list))
        return dumps(data_list), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
