from datetime import datetime

import torchvision.transforms as transforms
import cv2
from bson.json_util import dumps

import model.Initializer
import io
import numpy as np
from flask import Response, request, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import utils
from app.patients import bp
from app.utils.preprocess import generate_patch_image, adj_bb, preprocess, display_output
from config import Config


@bp.route('/')
def index():
    return "home"


# @bp.route('/prediction', methods=['GET'])
# def display_prediction():
#     depth_image = np.load("inputs/depth.npy")
#     pressure_image = np.load("inputs/pressure.npy")
#     funeNet = model.Initializer.initialize_model()
#     processed_image, image_patch = preprocess(depth_image, pressure_image)
#     pred = funeNet(processed_image)
#     return display_output(pred, image_patch)

@bp.route('/prediction', methods=['POST'])
def display_prediction():
    depth_image = np.load("inputs/depth.npy")
    pressure_image = np.load("inputs/pressure.npy")
    funeNet = model.Initializer.initialize_model()
    processed_image, image_patch = preprocess(depth_image, pressure_image)
    pred = funeNet(processed_image)
    return display_output(pred, image_patch)


@bp.route('/registration', methods=['POST'])
def register_patient():
    data = request.get_json()
    data["date_of_birth"] = datetime.combine(datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date(),
                                             datetime.min.time())
    # data["admitted_time"] = int(datetime.strptime(data["admitted_time"], "%Y-%m-%d %H:%M:%S").timestamp())
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
