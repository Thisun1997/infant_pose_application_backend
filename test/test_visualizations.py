import json
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from config import Config
from test_base import BaseTestCase


class VisualizationsTest(BaseTestCase):
    test_base_path = Config.base_path + "test/data/"
    f = open(test_base_path + 'visualizations_data.json')
    visualization_data = json.load(f)

    def setUp(self):
        super().setUp()
        self.insert_id = Config.visualization_collection.insert_one(self.visualization_data).inserted_id

    def test_display_prediction(self):
        depth_array = np.load(self.test_base_path + "depth.npy")
        pressure_array = np.load(self.test_base_path + "pressure.npy")

        data = {
            "patient_id": 1,
            "depth": depth_array.tolist(),
            "pressure": pressure_array.tolist(),
            "time": 1716869467770290100,
            "user": "user1"
        }
        response = self.app.post("visualizations/prediction", json=data)
        result = Config.visualization_collection.find_one({"patient_id": 1, "time": 1716869467770290100})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], str(result["_id"]))

    @patch('config.Config.visualization_collection.insert_one')
    def test_display_prediction_exception(self, mock_insert_one):
        mock_insert_one.side_effect = Exception("Mocked Exception")
        depth_array = np.load(self.test_base_path + "depth.npy")
        pressure_array = np.load(self.test_base_path + "pressure.npy")
        data = {
            "patient_id": 1,
            "depth": depth_array.tolist(),
            "pressure": pressure_array.tolist(),
            "time": 1716869467770290100,
            "user": "user1"
        }
        response = self.app.post("visualizations/prediction", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal error occurred", response.json['message'])

    def test_update_document_success(self):
        data = {
            "query": {
                "_id": str(self.insert_id)
            },
            "new_field": {
                "medical_remark": "test_medical_remark"
            }
        }
        response = self.app.put("visualizations/update", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], 'Record updated successfully')

    def test_update_document_error_invalid_input(self):
        data = {
            "query": {
                "_id": str(self.insert_id)
            },
            "new_field": {}
        }
        response = self.app.put("visualizations/update", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Invalid input")

    def test_update_document_error_not_found(self):
        data = {
            "query": {
                "_id": "6689507c72549bcf10113086"
            },
            "new_field": {
                "medical_remark": "test_medical_remark"
            }
        }
        response = self.app.put("visualizations/update", json=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Record not found")

    @patch('config.Config.visualization_collection.update_one')
    def test_update_document_exception(self, mock_update_one):
        mock_update_one.side_effect = Exception("Mocked Exception")
        data = {
            "query": {
                "_id": str(self.insert_id)
            },
            "new_field": {
                "medical_remark": "test_medical_remark"
            }
        }
        response = self.app.put("visualizations/update", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal error occurred", response.json['message'])

    def test_get_visualization_data(self):
        data = {"_id": str(self.insert_id)}
        response = self.app.get("visualizations/visualization_data", json=data)
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["patient_id"], self.visualization_data["patient_id"])

    @patch('config.Config.visualization_collection.find_one')
    def test_get_visualization_data_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        data = {"_id": str(self.insert_id)}
        response = self.app.get("visualizations/visualization_data", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal error occurred", response.json['message'])

    def test_get_history_data_success(self):
        data = {
            "from_time": "2024-07-06",
            "to_time": "2024-07-06",
            "patient_id": 5
        }
        response = self.app.get("visualizations/history_data", json=data)
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["patient_id"], self.visualization_data["patient_id"])

    def test_get_history_data_time_error(self):
        data = {
            "from_time": "2024-07-07",
            "to_time": "2024-07-06",
            "patient_id": 5
        }
        response = self.app.get("visualizations/history_data", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], 'Time range is invalid')

    def test_get_history_data_no_data(self):
        data = {
            "from_time": "2024-07-07",
            "to_time": "2024-07-07",
            "patient_id": 5
        }
        response = self.app.get("visualizations/history_data", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], 'No historical data available')

    @patch('config.Config.visualization_collection.find')
    def test_get_history_data_exception(self, mock_find):
        mock_find.side_effect = Exception("Mocked Exception")
        data = {
            "from_time": "2024-07-06",
            "to_time": "2024-07-06",
            "patient_id": 5
        }
        response = self.app.get("visualizations/history_data", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal error occurred", response.json['message'])


