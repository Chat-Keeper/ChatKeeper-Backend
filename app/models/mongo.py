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
        '''
        Mongo.speakers.create_index([("user_id", ASCENDING), ("name", ASCENDING)], unique=True)

        Mongo.speakers.drop_index("user_id_1_name_1")

        # 2. 在 speaker_qq 字段上创建一个唯一索引
        #    参数格式：列表内是 (字段名, 索引方向) 的元组；unique=True 表示唯一索引
        Mongo.speakers.create_index(
            [("speaker_qq", 1)],
            unique=True
        )
'''

        # 挂载到app上
        app.mongo_client = client
        app.mongo_db = db
        return app
