from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from app.models.user import User

class Token:
        
        @staticmethod
        def insert(token):
            
            User.tokens.insert_one(token)
            result = User.tokens.find_one({'token': token['token']})
            return result
        
        @staticmethod
        def destroy(user_id):

            result = User.tokens.delete_one({"user_id": user_id})

            return result.deleted_count == 1  #成功返回true,失败返回false
        
        @staticmethod
        def refresh(user_id, new_time):
            result = User.users.find_one({'user_id': user_id})
            if result is None:
                return None
            
            User.tokens.update_one(
                {"user_id": user_id},          # 集合里存储的也是字符串
                {"$set": {"expires_at": new_time}}
            )
            return result
        
        @staticmethod
        def find_user(username):
            user = User.users.find_one({'username': username})
            if user is None:
                return None
            
            result = User.tokens.find_one({"user_id": user['user_id']})
            return result
        
        @staticmethod
        def get_token(token: str):
            result = User.tokens.find_one({"token": token})
            if result is None:
                return None
            return result
        
            
        
            