import asyncio
from pymongo.mongo_client import MongoClient
from typing import Union
import certifi

async def get_guild_information(client: MongoClient, guild_id: int) -> dict: ###
    db = client["DIplos"]
    collection = db["new_guilds"]
    return collection.find_one({"guild_id": guild_id})

async def get_all_tokens_by_id(client: MongoClient, collection_id: str, token_ids: list) -> [dict]:
    db = client["DIplos"]
    collection = db["rarity"]

    tokens = []
    for token_id in token_ids:
        user_data = collection.find_one({"collection_id": collection_id, "token_id": token_id})
        if user_data:
            tokens.append(user_data)

    return tokens