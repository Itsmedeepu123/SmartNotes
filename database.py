
from pymongo import MongoClient
import os

MONGO_URL = 

client = MongoClient(MONGO_URL)
db = client["NotesDB"]

user_collection = db["users"]
note_collection = db["notes"]
