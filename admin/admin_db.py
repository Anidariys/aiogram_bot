from database.database import db


def get_ids_from_decision_list() -> list[int] | None:
    collection = db["decision"]
    users_id = [data["user_id"] for data in collection.find({}, {"_id": 0})]
    if users_id:
        return users_id
    return []


def get_from_decision_list(id: int) -> dict | None:
    collection = db["decision"]
    data = collection.find_one({"user_id": id}, {"_id": 0})
    return data

def add_to_decision_list(data):
    collection = db["decision"]
    collection.insert_one(data)


def delete_from_decision_list(user_id: int) -> None:
    collection = db["decision"]
    collection.delete_one({"user_id": user_id})


def get_white_list_users() -> list:
    collection = db["white_list"]
    white_users = [data for data in collection.find({}, {"_id": 0})]
    return white_users


def add_user_in_white_list(data: list) -> None:
    collection = db["white_list"]
    collection.insert_one(data)        


def delete_user_from_white_list(user_id: int) -> None:
    collection = db["white_list"]
    collection.delete_one({"user_id": user_id})
