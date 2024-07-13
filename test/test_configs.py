import os

import mongomock


basedir = os.path.abspath(os.path.dirname(__file__))


class TestConfig:
    client = mongomock.MongoClient()
    db = client['infant_pose_visualizer_system']  # Replace with your MongoDB database name
    users_collection = db['users']
    patients_collection = db['patients']
    counters_collection = db['counters']
    admissions_collection = db['admissions']
    visualization_collection = db['visualizations']
    feedback_collection = db['feedback']
    model_collection = db['models']
    base_path = "D:/IIT/academic/Final_project/code/infant_pose_application_backend/"

