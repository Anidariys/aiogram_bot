from pymongo import MongoClient
from config_data.config import load_config


config = load_config()
db_con = config.tg_bot.mongo_con

cluster = MongoClient(db_con)
db = cluster["vi_db"]


def get_all_users(name: str, group: str):
    collection = db[group]
    query = {"name": {"$regex": "^" + name, "$options": "i"}}
    users = collection.find(query, {"_id": 0})
    print(users)
    return [user for user in users]


def get_user(name: str, group: str) -> list:
    collection = db[group]
    myquery = {"name": {"$regex": name}}
    return collection.find_one(myquery, {"_id": 0})


def create_user(data: dict[str, str]) -> None | dict:
    user = get_user(data["name"], data["group"])
    if user:
        return user
    collection = db[data["group"]]
    del data["group"]
    collection.insert_one(data)


def update_user(data: dict[str, str]) -> None:
    collection = db[data["group"]]
    del data["group"]
    collection.find_one_and_update(
        {"name": data["name"]}, {"$set": {data["key"]: data["value"]}})


def delete_client(name: str, group: str) -> None:
    collection = db[group]
    collection.delete_one({"name": name})
