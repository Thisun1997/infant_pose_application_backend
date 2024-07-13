import json
from unittest import TestCase
from unittest.mock import patch

from config import Config
from test_base import BaseTestCase


class PatientsTest(BaseTestCase):
    patient_data = [
        {"_id": 1, "patient_name": "patient1", "gender": "Male",
         "date_of_birth": "2024-06-16T00:00:00.000Z", "guardian": "guardian1",
         "address": "address1", "contact_number": "0744444444"},
        {"_id": 2, "patient_name": "patient2", "gender": "Female",
         "date_of_birth": "2024-05-16T00:00:00.000Z", "guardian": "guardian2",
         "address": "address2", "contact_number": "0744444444"}
    ]

    counters_data = {"_id":"document_id","seq":2}

    def setUp(self):
        super().setUp()
        Config.patients_collection.insert_many(self.patient_data)
        Config.counters_collection.insert_one(self.counters_data)

    def test_index(self):
        response = self.app.get("patients/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        for i in range(len(response.json)):
            self.assertEqual(len(response.json[i]),2)
            self.assertEqual(response.json[i]["_id"],self.patient_data[i]["_id"])
            self.assertEqual(response.json[i]["patient_name"],self.patient_data[i]["patient_name"])

    @patch('config.Config.patients_collection.find')
    def test_index_exception(self, mock_find):
        mock_find.side_effect = Exception("Mocked Exception")
        response = self.app.get("patients/")
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['error'])

    def test_register_patient(self):
        data = {"patient_name": "patient3", "gender": "Male", "date_of_birth": "2024-04-16", "guardian": "guardian3"}
        response = self.app.post("patients/registration", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Registration successful!. Patient registration number is 3")

    @patch('config.Config.patients_collection.insert_one')
    def test_register_patient_exception(self, mock_insert_one):
        mock_insert_one.side_effect = Exception("Mocked Exception")
        data = {"patient_name": "patient3", "gender": "Male", "date_of_birth": "2024-04-16", "guardian": "guardian3"}
        response = self.app.post("patients/registration", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])

    def test_get_patient_success(self):
        data = {"_id":1}
        response = self.app.get("patients/data", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), self.patient_data[0])

    @patch('config.Config.patients_collection.find_one')
    def test_get_patient_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        data = {"_id":1}
        response = self.app.get("patients/data", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])

    def test_update_patient_document_success(self):
        new_contact_number = "0999999999"
        data = {"query": {"_id":2}, "new_field": {"contact_number": new_contact_number}}
        response = self.app.put("patients/update_data", json=data)
        self.assertEqual(response.status_code, 200)
        record = Config.patients_collection.find_one(data["query"])
        self.assertEqual(record["contact_number"], new_contact_number)

    def test_update_patient_document_error_invalid_input(self):
        data = {"query": {"_id":4}, "new_field": {}}
        response = self.app.put("patients/update_data", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Invalid input")

    def test_update_patient_document_error_not_found(self):
        data = {"query": {"_id":4}, "new_field": {"contact_number": "0999999999"}}
        response = self.app.put("patients/update_data", json=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "Record not found")

    @patch('config.Config.patients_collection.update_one')
    def test_update_patient_document_exception(self, mock_update_one):
        mock_update_one.side_effect = Exception("Mocked Exception")
        new_contact_number = "0999999999"
        data = {"query": {"_id":2}, "new_field": {"contact_number": new_contact_number}}
        response = self.app.put("patients/update_data", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])

