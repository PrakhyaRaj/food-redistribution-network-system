from pymongo import MongoClient

try:
    client = MongoClient(
        "mongodb://myUser:MyPass123@localhost:27017/?authSource=admin"
    )
    print("Connected! Databases:", client.list_database_names())
except Exception as e:
    print("Auth failed:", e)
