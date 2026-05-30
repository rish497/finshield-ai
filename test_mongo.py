from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")

print("Connecting...")

client = MongoClient(uri)

db = client["finshield"]

print(db.list_collection_names())

print("Mongo connected!")