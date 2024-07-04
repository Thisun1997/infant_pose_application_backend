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


@bp.route('/update_data', methods=['PUT'])
def update_patient_document():
    try:
        data = request.json
        query = data.get('query')
        query["_id"] = int(query["_id"])
        new_field = data.get('new_field')
        print(data)

        if not query or not new_field:
            return jsonify({"error": "Invalid input"}), 400

        result = Config.patients_collection.update_one(
            query,
            {"$set": new_field}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Record not found"}), 404

        return jsonify({"message": "Record updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
