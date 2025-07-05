from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient, ASCENDING

class Mongo:
    users = None
    tokens = None
    groups = None
    speakers = None

    @staticmethod
    def init_mongo(app):
        # 1. 建立连接
        connection_string = "mongodb://localhost:27017/"

        client = MongoClient(connection_string)
        db = client["ChatKeeper"]

        Mongo.users = db["users"]
        Mongo.tokens = db["tokens"]

        Mongo.groups = db["groups"]
        Mongo.speakers = db["speakers"]

        # 对 user_id、token、chat_id 做索引加速查询
        Mongo.users.create_index("user_id", unique=True)
        Mongo.tokens.create_index("token", unique=True)
        Mongo.groups.create_index("group_id", unique=True)
        Mongo.speakers.create_index("speaker_id", unique=True)
        

        # 挂载到app上
        app.mongo_client = client
        app.mongo_db = db
        return app
