from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")

async def get_db():
    client = MongoClient(MONGODB_URI)
    main_db = client["linq"]
    return main_db
