import unittest
from unittest.mock import patch

from config import Config
from test_base import BaseTestCase


class FeedbackTest(BaseTestCase):
    feedback_data = [
        {"feedback": "specific_feedback", "user": "test1", "time": "1720274255172264600",
         "vis_insertion_id": "66894d3e72549bcf10113082"},
        {"feedback": "general_feedback", "user": "test1", "time": "1720272757552567800"}
    ]

    def setUp(self):
        super().setUp()
        for feedback in self.feedback_data:
            if "_id" in feedback: del feedback["_id"]
        Config.feedback_collection.insert_many(self.feedback_data)

    def test_index(self):
        response = self.app.get("feedback/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        for feedback in self.feedback_data:
            feedback["_id"] = str(feedback["_id"])
        self.assertEqual(response.json, self.feedback_data[::-1])

    @patch('config.Config.feedback_collection.find')
    def test_index_exception(self, mock_find):
        mock_find.side_effect = Exception("Mocked Exception")
        response = self.app.get("feedback/")
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['error'])

    def test_add_feedback(self):
        data = {"feedback": "general_feedback_2", "user": "test1", "time": "1720272757552588700"}
        response = self.app.post("feedback/add", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], 'feedback submitted successfully')

    @patch('config.Config.feedback_collection.insert_one')
    def test_add_feedback_exception(self, mock_insert_one):
        mock_insert_one.side_effect = Exception("Mocked Exception")
        data = {"feedback": "general_feedback_2", "user": "test1", "time": "1720272757552588700"}
        response = self.app.post("feedback/add", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])

    def test_get_feedback_available(self):
        data = {"vis_insertion_id": "66894d3e72549bcf10113082"}
        response = self.app.get("feedback/get", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "specific_feedback")

    def test_get_feedback_not_available(self):
        data = {"vis_insertion_id": "test"}
        response = self.app.get("feedback/get", json=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["message"], "-")

    @patch('config.Config.feedback_collection.find_one')
    def test_get_feedback_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        data = {"vis_insertion_id": "test"}
        response = self.app.get("feedback/get", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])


if __name__ == '__main__':
    unittest.main()
