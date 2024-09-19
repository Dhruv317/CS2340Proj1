# mongo_connector.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
# Define your MongoDB connection URI and database
MONGODB_CONNECTION_URI = os.getenv('MONGODB_CONNECTION_URI')

def get_mongo_connection():
    client = MongoClient(MONGODB_CONNECTION_URI)
    db = client['2340']
    return db

