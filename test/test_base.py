from unittest import TestCase

from app import app
from config import Config
from test_configs import TestConfig


class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['Testing'] = True
        # Override the real database collections with the mock ones
        Config.client = TestConfig.client
        Config.db = TestConfig.db
        Config.users_collection = TestConfig.users_collection
        Config.patients_collection = TestConfig.patients_collection
        Config.counters_collection = TestConfig.counters_collection
        Config.admissions_collection = TestConfig.admissions_collection
        Config.visualization_collection = TestConfig.visualization_collection
        Config.feedback_collection = TestConfig.feedback_collection
        Config.model_collection = TestConfig.model_collection

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        # Clean up the mock database after each test
        Config.db.drop_collection('users')
        Config.db.drop_collection('patients')
        Config.db.drop_collection('counters')
        Config.db.drop_collection('admissions')
        Config.db.drop_collection('visualizations')
        Config.db.drop_collection('feedback')
        Config.db.drop_collection('models')