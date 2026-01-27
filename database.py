
from pymongo import MongoClient

MONGO_URL = "mongodb+srv://deepa:deepa123@cluster0.ppja1aq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URL)
db = client["NotesDB"]

user_collection = db["users"]
note_collection = db["notes"]
