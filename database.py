
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("mongodb+srv://deepa:deepa123@cluster0.ppja1aq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URL)

db = client["NotesDB"]

user_collection = db["users"]
note_collection = db["notes"]
counter_collection = db["counters"]   # ✅ new: for auto note id
