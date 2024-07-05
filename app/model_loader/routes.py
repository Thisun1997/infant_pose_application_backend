import importlib

from bson import ObjectId
from bson.json_util import dumps
from flask import jsonify, request

from app.model_loader import bp
from config import Config

try:
    import model.Initializer

    model_configs = Config.model_collection.find_one({"status": "Active"})
    fuseNet = model.Initializer.initialize_model(model_configs)
except Exception as e:
    print(e)


@bp.route('/', methods=['GET'])
def index():
    try:
        records = Config.model_collection.find()
        result = []
        for record in records:
            record['_id'] = str(record['_id'])
            result.append(record)
        return jsonify(result[::-1]), 200
    except Exception as e:
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

        for key, value in data.items():
            print(key)
            query = {"_id": ObjectId(value)}
            status = ""
            if key == "activate_id":
                status = "Active"
            result = Config.model_collection.update_one(
                query,
                {"$set": {"status": status}}
            )
            if result.matched_count == 0:
                return jsonify({"message": "Model to " + status.lower() + " not found"}), 404

        return jsonify({"message": "Model activate successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500


@bp.route('/get_model', methods=['GET'])
def get_active_model():
    try:
        data = request.json
        data["_id"] = ObjectId(data["_id"])
        active_model_configs = Config.model_collection.find_one(data)
        return dumps(active_model_configs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
