import json
import unittest
from unittest.mock import patch

from config import Config
from test_base import BaseTestCase


class ModelLoaderTests(BaseTestCase):
    model_data = [
        {"model_type": "HRNet_fusion", "status": "Active", "fuse_stage": 2, "fuse_type": "iAFF",
         "model_name": "HRNet-2-iAFF", "best_model_path": "model_best.pth"},
        {"model_type": "HRNet_fusion", "status": "", "fuse_stage": 3, "fuse_type": "iAFF", "model_name": "HRNet-3-iAFF",
         "best_model_path": "model_best_3_iAFF.pth"}
    ]

    def setUp(self):
        super().setUp()
        for model in self.model_data:
            if "_id" in model: del model["_id"]
        Config.model_collection.insert_many(self.model_data)

    def test_index(self):
        response = self.app.get('model_loader/')
        result = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)
        for model in self.model_data:
            model["_id"] = str(model["_id"])
        self.assertEqual(result, self.model_data[::-1])

    @patch('config.Config.model_collection.find')
    def test_index_exception(self, mock_find):
        mock_find.side_effect = Exception("Mocked Exception")
        response = self.app.get('model_loader/')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['error'])

    def test_update_model_success(self):
        records = Config.model_collection.find()
        data = {}
        for record in records:
            if record["status"] == "Active":
                data["deactivate_id"] = str(record["_id"])
            else:
                data["activate_id"] = str(record["_id"])
        response = self.app.put('model_loader/update_model', json={"query": data})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Model activate successfully")
        records = Config.model_collection.find()
        for record in records:
            if record["status"] == "Active":
                self.assertEqual(str(record["_id"]), data["activate_id"])
            else:
                self.assertEqual(str(record["_id"]), data["deactivate_id"])

    def test_update_model_error_activate_not_found(self):
        data = {
            "activate_id" : "664fa35a0e5a9ec4a8786e6d",
            "deactivate_id" : "66504061fd45155259a23acb"
        }
        response = self.app.put('model_loader/update_model', json={"query": data})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Model to activate not found")

    def test_update_model_error_deactivate_not_found(self):
        data = {
            "deactivate_id" : "664fa35a0e5a9ec4a8786e6d"
        }
        records = Config.model_collection.find()
        for record in records:
            if record["status"] != "Active":
                data["activate_id"] = str(record["_id"])
                break
        response = self.app.put('model_loader/update_model', json={"query": data})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Model to deactivate not found")

    @patch('config.Config.model_collection.find_one')
    def test_update_model_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        records = Config.model_collection.find()
        data = {}
        for record in records:
            if record["status"] == "Active":
                data["deactivate_id"] = str(record["_id"])
            else:
                data["activate_id"] = str(record["_id"])
        response = self.app.put('model_loader/update_model', json={"query": data})
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])

    def test_get_active_model(self):
        records = Config.model_collection.find()
        for record in records:
            if record["status"] == "Active":
                active_model_configs = record
                break
        response = self.app.get('model_loader/get_model', json={"_id": str(active_model_configs["_id"])})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        result["_id"] = result["_id"]["$oid"]
        active_model_configs["_id"] = str(active_model_configs["_id"])
        self.assertEqual(result, active_model_configs)

    @patch('config.Config.model_collection.find_one')
    def test_get_active_model_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        records = Config.model_collection.find()
        for record in records:
            if record["status"] == "Active":
                active_model_configs = record
                break
        response = self.app.get('model_loader/get_model', json={"_id": str(active_model_configs["_id"])})
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['error'])


if __name__ == '__main__':
    unittest.main()
