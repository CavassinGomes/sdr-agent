from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from config import settings

uri = settings.MONGO_URI

_client = None
_db = None

def get_db():
    global _client, _db
    if _client is None:
        try:
            _client = MongoClient(uri)
            _db = _client.get_default_database()
        except ConnectionFailure:
            print("Failed to connect to MongoDB.")
            raise
    return _db

        