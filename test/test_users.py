import unittest
from unittest.mock import patch

from test_base import BaseTestCase

from config import Config


class UsersTests(BaseTestCase):

    def test_authenticate_user_success(self):
        Config.users_collection.insert_one(
            {"username": "testuser", "password": "$2b$12$O.kd61ABfBw3/4tYoSyMbO56V9mnN3embX5gstBFDT3EVSbigK/3i",
             "user_type": 1})
        response = self.app.post('/users/auth', json={"username": "testuser", "password": "test", "user_type": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "login success")

    def test_authenticate_user_error(self):
        response = self.app.post('/users/auth', json={"username": "testuser", "password": "test", "user_type": 2})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Incorrect Username, Password and User type combination")

    @patch('config.Config.users_collection.find_one')
    def test_authenticate_user_exception(self, mock_find_one):
        mock_find_one.side_effect = Exception("Mocked Exception")
        response = self.app.post('/users/auth', json={"username": "testuser", "password": "test", "user_type": 2})
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mocked Exception', response.json['message'])


if __name__ == '__main__':
    unittest.main()
