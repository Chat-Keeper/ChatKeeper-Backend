from datetime import datetime
from typing import Any
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy

Mongo = LocalProxy(lambda: current_app.mongo_db)

class Token:
    '''
            token = {
                "token": create_token(),
                "user_id": user_id,
                "expires_at": expires_at
            }
    '''

    @staticmethod
    def insert(token):
        Mongo.tokens.insert_one(token)
        result = Mongo.tokens.find_one({'token': token['token']})
        return result

    @staticmethod
    def destroy(user_id):
        result = Mongo.tokens.delete_one({"user_id": user_id})
        return result.deleted_count == 1  # 成功返回true, 失败返回false

    @staticmethod
    def refresh(user_id, new_time):
        user = Mongo.users.find_one({'user_id': user_id})
        if user is None:
            return None

        Mongo.tokens.update_one(
            {"user_id": user_id},  # 集合里存储的也是字符串
            {"$set": {"expires_at": new_time}}
        )
        result = Mongo.tokens.find_one({'user_id': user_id})
        return result

    @staticmethod
    def find_user(user_id):
        user = Mongo.users.find_one({'user_id': user_id})  # 查找是否有user_id匹配
        if user is None:
            return None

        result = Mongo.tokens.find_one({"user_id": user['user_id']})  # 返回对应令牌
        return result

    @staticmethod
    def getuser(token: str) -> str | None:
        token = Mongo.tokens.find_one({'token': token})
        if token is None:
            return None
        return token['user_id']

    @staticmethod
    def get_token(token: str):
        result = Mongo.tokens.find_one({"token": token})
        if result is None:
            return None
        return result

        
            