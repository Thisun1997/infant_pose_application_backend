import os

from pymongo import MongoClient, ReturnDocument

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
    #     or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # app.secret_key = "your_secret_key"  # Replace with a strong secret key
    client = MongoClient('localhost', 27017)
    db = client['infant_pose_visualizer_system']  # Replace with your MongoDB database name
    users_collection = db['users']
    patients_collection = db['patients']
    counters_collection = db['counters']
    admissions_collection = db['admissions']
    visualization_collection = db['visualizations']
    feedback_collection = db['feedback']

