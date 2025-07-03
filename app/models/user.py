from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient, ASCENDING
from flask import current_app
from werkzeug.local import LocalProxy

Mongo = LocalProxy(lambda: current_app.mongo)

class User:

    '''
    {
            "user_id": user_id,
            "username": username,
            "password": password,    
            "created_at": datetime.utcnow()
        }
    '''
    @staticmethod
    #1. 检查数据库中是否已经存在该用户
    def find(username):

        user = Mongo.users.find_one({'username': username})
        if user:
            return user
        else:
            return None

    @staticmethod
        # 2. 创建一个新用户
    def insert(new_user):
        user_id = str(uuid4())
        username = new_user['username']
        password = new_user['password']
        Mongo.users.insert_one({
            "user_id": user_id,
            "username": username,
            "password": password,    
            "created_at": datetime.utcnow()
        })
        result = Mongo.users.find_one({'user_id': user_id})
        
        '''
        #生成登录令牌
        token = str(uuid4())
        ttl_minutes = 10  #登录失效时间
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        User.tokens.insert_one({
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at
        })
        '''
        return result

    '''
    @staticmethod
    # 4. 导入一条聊天记录
    def import_chat(user_id, messages):

        chat_id = str(uuid4())
        speakers_list = sorted({ msg["speaker"] for msg in messages })
        User.chats.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "imported_at": datetime.utcnow(),
            "n_messages": len(messages),
            "speakers": speakers_list,
            "messages": messages
        })
        return chat_id
        '''
    '''
    @staticmethod
    # 6. 更新 speakers 集合
    #def update_speakers_for_chat(chat_id):
        chat = User.chats.find_one({"chat_id": chat_id})
        if not chat:
            raise ValueError("找不到对应聊天记录")
        user_id = chat["user_id"]

        # 按发言人分组收集文本
        from collections import defaultdict
        buf = defaultdict(list)
        for msg in chat["messages"]:
            buf[msg["speaker"]].append(msg["text"])

        now = datetime.utcnow()
        for name, texts in buf.items():
            analysis = analyze_personality(texts)
            speakers.update_one(
                {"user_id": user_id, "name": name},
                {
                    "$set": {
                        "last_analyzed_at": now,
                        "trait": analysis["trait"],
                        "interest": analysis["interest"]
                    }
                },
                upsert=True
            )
            '''




