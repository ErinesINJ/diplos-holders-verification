import asyncio
from pymongo.mongo_client import MongoClient
from typing import Union
import certifi

async def find_user_wallet_in_db(client: MongoClient, user_id: str) -> Union[str, None]:
    db = client["DIplos"]
    collection = db["guilds"]

    user_data = collection.find_one({"user_ID": user_id})
    
    if user_data:
        return user_data.get("wallets", [])
    else:
        return None

async def get_all_user_ids(client: MongoClient) -> [str]:
    db = client["DIplos"]
    collection = db["guilds"]

    user_ids = []
    for user_data in collection.find({}, {"user_ID": 1}):
        user_ids.append(user_data["user_ID"])

    return user_ids