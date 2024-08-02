from pymongo.database import Database
from .models import UserCreate, UserInDB

async def get_user(db: Database, username: str):
    users_collection = db['users']
    if   users_collection == None:
        return None
    return db["users"].find_one({"username": username})

async def get_user_by_email(db: Database, email: str):
    users_collection = db['users']
    if users_collection == None:
        return None
    return  db["users"].find_one({"email": email})

async def create_user(db: Database, user: UserCreate):
    user_dict = user.model_dump()
    user_dict["hashed_password"] = user_dict.pop("password")
    db["users"].insert_one(user_dict)
    return user_dict

async def edit_user(db: Database, user_id: str, update_data: dict):
    db["users"].update_one({"username": user_id}, {"$set": update_data})
    return  db["users"].find_one({"username": user_id})

async def delete_user(db: Database, user_id: str):
    return  db["users"].delete_one({"username": user_id})

