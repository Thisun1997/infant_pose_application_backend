import os

from pymongo import MongoClient, ReturnDocument

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    client = MongoClient('localhost', 27017)
    db = client['infant_pose_visualizer_system']  # Replace with your MongoDB database name
    users_collection = db['users']
    patients_collection = db['patients']
    counters_collection = db['counters']
    admissions_collection = db['admissions']
    visualization_collection = db['visualizations']
    feedback_collection = db['feedback']
    model_collection = db['models']

